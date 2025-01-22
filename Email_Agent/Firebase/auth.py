import firebase_admin
from firebase_admin import credentials, firestore
import os

def authenticate_firebase():
    """
    Authenticate to Firebase and return the Firestore client.

    Returns:
        firestore.Client: The Firestore client if authentication is successful, None otherwise.
    """
    try:
        # Get the absolute path to the service account key
        current_dir = os.path.dirname(os.path.abspath(__file__))
        key_path = os.path.join(current_dir, 'emailmanager-2b0b7-firebase-adminsdk-fbsvc-1430ac2a15.json')
        
        # Check if Firebase app is already initialized
        if not firebase_admin._apps:
            # Use a service account
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Failed to authenticate with Firebase: {e}")
        return None