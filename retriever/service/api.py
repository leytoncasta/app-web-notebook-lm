import requests
from pathlib import Path
import os
from dotenv import load_dotenv

SERVICE_ABSOLUTE_PATH = Path(__file__).resolve().parent
env_file = SERVICE_ABSOLUTE_PATH / '.env'
load_dotenv(env_file)

API_URL_AUGMENTER = os.getenv("API_URL_AUGMENTER")
if not API_URL_AUGMENTER:
    raise ValueError("API_URL_AUGMENTER environment variable is not set")

# Make a POST request to an API endpoint
def post_contexts(payload):
    try:
        response = requests.post(API_URL_AUGMENTER, json=payload)

        # Check if the request was successful (status code 201 for created)
        if response.status_code == 201:
            # Parse the response as JSON
            data = response.json()
            return data
        else:
            return f"Failed to consume augmenter service. Status code: {response.status_code}"

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    except ValueError as err:
        print(f"Invalid Json Response: {err}")