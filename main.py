from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Union
from openai import OpenAI
import os
import json

app = FastAPI()

# Define the Pydantic models for the response
class Criterion(BaseModel):
    criterion: str
    details: str #Union[str, None] = None

class AssessmentResponse(BaseModel):
    criteria_met: List[Criterion]
    qualification_rating: str

# Enter your own OpenAI API key as OS environment
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)

# Helper function to call OpenAI API and process the CV
def analyze_cv(cv_text: str):
    # Define the prompt for the OpenAI API based on the given criteria
    prompt = f"""
    Analyze the following CV and determine if the person meets the criteria for an O-1A visa. 
    For each of the 8 criteria, list all the achievements related to that criterion with specific details from the CV.

    Criteria:
    1. Awards - Documentation of the beneficiary's receipt of nationally or internationally recognized prizes or awards for excellence in the field of endeavor.
    2. Membership - Documentation of the beneficiary's membership in associations in the field for which classification is sought, which require outstanding achievements of their members, as judged by recognized national or international experts in their disciplines or fields.
    3. Press - Published material in professional or major trade publications or major media about the beneficiary, relating to the beneficiary's work in the field for which classification is sought. This evidence must include the title, date, and author of such published material and any necessary translation.
    4. Judging - Evidence of the beneficiary's participation on a panel, or individually, as a judge of the work of others in the same or in an allied field of specialization for which classification is sought.
    5. Original contribution - Evidence of the beneficiary's original scientific, scholarly, or business-related contributions of major significance in the field.
    6. Scholarly articles - Evidence of the beneficiary's authorship of scholarly articles in the field, in professional journals, or other major media.
    7. Critical employment - Evidence that the beneficiary has been employed in a critical or essential capacity for organizations and establishments that have a distinguished reputation.
    8. High remuneration - Evidence that the beneficiary has either commanded a high salary or will command a high salary or other remuneration for services as evidenced by contracts or other reliable evidence.

    CV:
    {cv_text}

    For each criterion that the person meets, for the "details" section: list the specific achievements with details, such as names of awards, membership organizations, titles of press articles, etc found in CV. Output the response in JSON format as follows:
    {{
        "criteria_met": [
            {{"criterion": "Awards", "details": "List of specific awards and details"}},
            {{"criterion": "Membership", "details": "List of specific memberships and details"}},
            {{"criterion": "Press", "details": "List of specific press articles and details"}},
            {{"criterion": "Judging", "details": "List of specific judging roles and details"}},
            {{"criterion": "Original contribution", "details": "List of specific original contributions and details"}},
            {{"criterion": "Scholarly articles", "details": "List of specific scholarly articles and details"}},
            {{"criterion": "Critical employment", "details": "List of specific critical employment roles and details"}},
            {{"criterion": "High remuneration", "details": "List of specific remuneration details"}}
        ]
    }}
    Make sure the JSON format is correct and provide detailed and specific information for each criterion. If the person does not meet a certain criteria, do not include in JSON output.
    """

    # Call the OpenAI API with the defined prompt
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=1500,
    )

    answer = response.choices[0].message.content
    return answer.strip()

# Helper function to parse OpenAI response and determine rating
def parse_analysis(analysis_result: str): 
    criteria = [
        "Awards",
        "Membership",
        "Press",
        "Judging",
        "Original contribution",
        "Scholarly articles",
        "Critical employment",
        "High remuneration"
    ]

    criteria_met = []
    try:
        analysis_json = json.loads(analysis_result)
        raw_criteria_met = analysis_json.get('criteria_met', [])

        for item in raw_criteria_met:
            criterion = item.get('criterion')
            details = item.get('details')
            
            # Attempt to parse the details field if it's a JSON string
            try:
                details_json = json.loads(details)
                details = details_json.get('details', details)
            except (json.JSONDecodeError, TypeError):
                pass
            
            criteria_met.append(Criterion(criterion=criterion, details=details))
        
        # Determine rating based on the number of criteria met
        num_criteria_met = len(criteria_met)
        if num_criteria_met >= 6:
            qualification_rating = "high"
        elif num_criteria_met >= 3:
            qualification_rating = "medium"
        else:
            qualification_rating = "low"
        
        return criteria_met, qualification_rating
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return [], 'error'

# Endpoint to assess the CV
@app.post("/assess_cv", response_model=AssessmentResponse)
async def assess_cv(file: UploadFile = File(...)):
    try:
        # Read the uploaded file
        cv_text = (await file.read()).decode("utf-8")

        # Analyze the CV using the helper function
        analysis_result = analyze_cv(cv_text)

        # Parse the analysis result to determine criteria met and rating
        criteria_met, qualification_rating = parse_analysis(analysis_result)

        response = AssessmentResponse(criteria_met=criteria_met, qualification_rating=qualification_rating)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
