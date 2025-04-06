import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()

# Check if we're in local development mode
IS_LOCAL_DEV = os.environ.get('DEBUG', 'false').lower() == 'true'

# Only import Secret Manager if we're not in local development mode
if not IS_LOCAL_DEV:
    try:
        from google.cloud import secretmanager
        # Initialize the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        # Hardcoded project ID
        PROJECT_ID = "primeval-truth-431023-f9"
        logger.info("Using Google Secret Manager for secrets")
    except Exception as e:
        logger.warning(f"Failed to initialize Secret Manager: {e}")
        IS_LOCAL_DEV = True
else:
    logger.info("Running in local development mode, using environment variables for secrets")

def get_secret(secret_name):
    logger.info(f"Attempting to retrieve secret: {secret_name}")
    
    # First check if the secret is available as an environment variable
    env_var = os.environ.get(secret_name)
    if env_var:
        logger.info(f"Retrieved secret {secret_name} from environment variables")
        return env_var
    
    # If not in local dev mode and environment variable not found, try Google Secret Manager
    if not IS_LOCAL_DEV:
        try:
            name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            payload = response.payload.data.decode("UTF-8")
            logger.info(f"Retrieved secret {secret_name} from Secret Manager")
            return payload
        except Exception as e:
            logger.error(f"Error retrieving secret {secret_name} from Secret Manager: {e}")
            # Fall back to environment variables
            logger.warning(f"Falling back to environment variables for {secret_name}")
    
    # If we're in local dev mode or Secret Manager failed, look for a default value
    if secret_name == "OPENAI_API_KEY":
        # Warn about missing API key
        logger.warning("OPENAI_API_KEY not found. Please set this in your environment or .env file.")
    
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
