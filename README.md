# O-1A Visa Qualification Assessment

This is a FastAPI application to assess a person's qualification for an O-1A immigration visa based on their CV. The application uses OpenAI's API to evaluate the CV against 8 criteria.

## Installation

1. Clone the repository:
   git clone https://github.com/ryandpeng/alma.git
   cd alma

2. Create a virtual enviroment and activate (MacOS):
    python3 -m venv venv
    source venv/bin/activate

2. Install the dependencies:
    pip3 install -r requirements.txt

3. Set your OpenAI API key as an environment variable:
    export OPENAI_API_KEY=<YOUR_API_KEY>

4. Run the application:
    uvicorn main:app --reload

5. Send a POST request to '/assess_cv' with the CV file to get assessment results. Use python script.
    python3 upload_cv.py