import unittest
from Email_Agent.Firebase.auth import authenticate_firebase
from Email_Agent.Firebase.upload_email import upload_sent_email

class TestFirebaseFunctions(unittest.TestCase):

    def setUp(self):
        """Set up the test case environment."""
        self.recipient_name = "Test User"
        self.draft_email = "This is a test email."
        self.user_uid = "test_user_uid"

    def test_authenticate_firebase(self):
        """Test the Firebase authentication function."""
        db = authenticate_firebase()
        self.assertIsNotNone(db, "Firebase authentication failed, db should not be None.")

    def test_upload_sent_email(self):
        """Test the upload_sent_email function."""
        result = upload_sent_email(self.recipient_name, self.draft_email, self.user_uid)
        self.assertTrue(result, "Email upload failed, result should be True.")

if __name__ == "__main__":
    unittest.main()
