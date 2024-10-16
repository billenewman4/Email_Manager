import sys
from google.cloud import secretmanager

# Initialize the Secret Manager client
client = secretmanager.SecretManagerServiceClient()

# Hardcoded project ID
PROJECT_ID = "primeval-truth-431023-f9"

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
        return None

# Example usage
if __name__ == "__main__":
    secret_name = 'SERPAPI_KEY'  # Replace with your actual secret name
    secret_value = get_secret(secret_name)
    if secret_value:
        print(f"Successfully retrieved secret {secret_name}", file=sys.stderr)
        # Don't print the actual secret value in logs
        print(f"The secret value for {secret_name} is [REDACTED]", file=sys.stderr)
    else:
        print(f"Failed to retrieve the secret {secret_name}", file=sys.stderr)
