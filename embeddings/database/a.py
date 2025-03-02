from dotenv import load_dotenv
import os
load_dotenv(override=True)
print(os.getenv("CONNECTION_STRING"))
