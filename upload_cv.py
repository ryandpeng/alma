import requests

url = "http://127.0.0.1:8000/assess_cv"
file_path = "/Users/ryanpeng/Desktop/Alma/example_cv.txt"  # Use correct CV file and path (might need to update)

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print(response.json())
