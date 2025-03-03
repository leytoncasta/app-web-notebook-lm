import aiohttp
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)

SERVICE_ABSOLUTE_PATH = Path(__file__).resolve().parent
env_file = SERVICE_ABSOLUTE_PATH / '.env'
load_dotenv(env_file)

API_URL_AUGMENTER = os.getenv("API_URL_AUGMENTER")
if not API_URL_AUGMENTER:
    raise ValueError("API_URL_AUGMENTER environment variable is not set")

# Make an async POST request to an API endpoint
async def post_contexts(payload):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL_AUGMENTER, json=payload) as response:
                # Check if the request was successful (status code 201 for created)
                if response.status == 201:
                    # Parse the response as JSON
                    data = await response.json()
                    return data
                else:
                    error_msg = f"Failed to consume augmenter service. Status code: {response.status}"
                    logger.error(error_msg)
                    return error_msg

    except aiohttp.ClientError as err:
        logger.error(f"HTTP error occurred: {err}")
        raise ValueError(f"HTTP error occurred: {err}")
    except ValueError as err:
        logger.error(f"Invalid Json Response: {err}")
        raise ValueError(f"Invalid Json Response: {err}")
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")
        raise ValueError(f"An unexpected error occurred: {err}")