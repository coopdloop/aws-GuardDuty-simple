import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
