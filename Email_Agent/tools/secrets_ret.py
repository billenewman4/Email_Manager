import os
import sys
from google.cloud import secretmanager
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the Secret Manager client
client = secretmanager.SecretManagerServiceClient()

# Hardcoded project ID
PROJECT_ID = "primeval-truth-431023-f9"

#Load environment variables
load_dotenv()

def get_secret(secret_name):
    logger.info(f"Attempting to retrieve secret: {secret_name}")
    
    # Check environment variables
    env_value = os.getenv(secret_name)
    if env_value:
        print(f"Found secret {secret_name} in environment variables")
        return env_value
    logger.info(f"Secret {secret_name} not found in environment variables")
    
    # Try Secret Manager
    if client:
        try:
            print(f"Attempting to retrieve {secret_name} from Secret Manager")
            name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode('UTF-8')
            logger.info(f"Successfully retrieved {secret_name} from Secret Manager")
            return secret_value
        except Exception as e:
            logger.error(f"Error accessing {secret_name} from Secret Manager: {str(e)}", exc_info=True)
            logger.error(f"Full error details:", exc_info=True)
    else:
        logger.error("Secret Manager client not initialized")
    
    return None

# Example usage
if __name__ == "__main__":
    secret_name = 'OpenAPI_KEY'  # Replace with your actual secret name
    secret_value = get_secret(secret_name)
    if secret_value:
        print(f"Successfully retrieved secret {secret_name}", file=sys.stderr)
        # Don't print the actual secret value in logs
        print(f"The secret value for {secret_name} is [REDACTED]", file=sys.stderr)
    else:
        print(f"Failed to retrieve the secret {secret_name}", file=sys.stderr)
