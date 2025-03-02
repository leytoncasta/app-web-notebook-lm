import requests
from pathlib import Path
import os
from dotenv import load_dotenv
from fastapi import HTTPException

SERVICE_ABSOLUTE_PATH = Path(__file__).resolve().parent
env_file = SERVICE_ABSOLUTE_PATH / '.env'
load_dotenv(env_file)

API_URL_LLM = os.getenv("API_URL_LLM")
if not API_URL_LLM:
    raise ValueError("API_URL_LLM environment variable is not set")

# Make a POST request to an API endpoint
def post_searching(payload):
        response = requests.post(API_URL_LLM, json=payload)
        # Check if the request was successful (status code 201 for created)
        if response.status_code >= 200 and response.status_code < 300:
            print("Successfully consumed llm service")  
        else:
            print(f"Failed to consume augmenter service. Status code: {response.status_code}")