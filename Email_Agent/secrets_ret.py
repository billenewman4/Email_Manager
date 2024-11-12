from dotenv import load_dotenv
import os

load_dotenv()  # This loads the variables from .env

def get_secret(secret_name):
    return os.getenv(secret_name)
