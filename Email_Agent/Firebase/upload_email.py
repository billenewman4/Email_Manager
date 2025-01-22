from .auth import authenticate_firebase
from firebase_admin import firestore

def upload_sent_email(recipient_name: str, draft_email: str, user_uid: str) -> bool:
    """
    Upload a sent email to the Firestore database.

    Args:
        recipient_name (str): The name of the email recipient.
        draft_email (str): The content of the email that was sent.
        user_uid (str): The UID of the user sending the email.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    # Get Firestore client using the auth module
    db = authenticate_firebase()
    if not db:
        print("Failed to authenticate with Firebase")
        return False

    # Reference to the 'sent_emails' collection
    collection_name = 'sent_emails'
    collection_ref = db.collection(collection_name)

    # Create a new document with the email details
    email_data = {
        "recipient_name": recipient_name,
        "draft_email": draft_email,
        "user_uid": user_uid,
        "timestamp": firestore.SERVER_TIMESTAMP  # Automatically set the timestamp
    }

    # Add the email data to the collection
    collection_ref.add(email_data)
    print(f"Successfully uploaded email to {recipient_name} for user {user_uid}")
    return True
