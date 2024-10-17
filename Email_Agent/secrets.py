import sys
import os
from google.cloud import secretmanager
from dotenv import load_dotenv

# Initialize the Secret Manager client
client = secretmanager.SecretManagerServiceClient()

# Hardcoded project ID
PROJECT_ID = "primeval-truth-431023-f9"

# Load environment variables from .env file
load_dotenv()

def get_secret(secret_name):
    print(f"Attempting to retrieve secret: {secret_name}", file=sys.stderr)
    
    try:
        # Try to get the secret from Secret Manager
        name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode('UTF-8')
        print(f"Successfully retrieved secret {secret_name} from Secret Manager", file=sys.stderr)
        return secret_value
    except Exception as e:
        print(f"Failed to access secret {secret_name} from Secret Manager: {str(e)}", file=sys.stderr)
        # If not found in Secret Manager, check .env file
        env_value = os.getenv(secret_name)
        if env_value:
            print(f"Retrieved secret {secret_name} from .env file", file=sys.stderr)
            return env_value
        else:
            print(f"Secret {secret_name} not found in .env file", file=sys.stderr)
            return None
