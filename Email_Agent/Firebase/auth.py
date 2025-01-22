import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

def authenticate_firebase():
    """
    Authenticate to Firebase and return the Firestore client.

    Returns:
        firestore.Client: The Firestore client if authentication is successful, None otherwise.
    """
    try:
        # Load service account credentials from Google Cloud Secret Manager
        from google.cloud import secretmanager

        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()

        # Access the secret version
        secret_name = "projects/primeval-truth-431023-f9/secrets/FIREBASE_CONFIG/versions/latest"
        response = client.access_secret_version(request={"name": secret_name})

        # Parse the secret payload
        service_account_info = json.loads(response.payload.data.decode("UTF-8"))

        # Check if Firebase app is already initialized
        if not firebase_admin._apps:
            # Use a service account
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Failed to authenticate with Firebase: {e}")
        return None