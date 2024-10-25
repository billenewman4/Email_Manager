import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from getpass import getpass

def create_email_draft(subject, body, recipient_email, sender_email):
    try:
        # Create the message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the body to the email
        msg.attach(MIMEText(body, 'plain'))

        # Convert the message to a string
        email_content = msg.as_string()

        # Save the draft to a file (simulating draft creation)
        draft_folder = os.path.join(os.path.expanduser("~"), "Email_Drafts")
        os.makedirs(draft_folder, exist_ok=True)
        draft_file = os.path.join(draft_folder, f"draft_{subject.replace(' ', '_')}.eml")

        with open(draft_file, 'w') as f:
            f.write(email_content)

        print(f"Draft message created successfully and saved to {draft_file}")
        return True
    except Exception as e:
        print(f"Unexpected error creating draft message: {str(e)}")
        return False

def main():
    print("Welcome to the Email Draft Creator!")
    
    # Use predefined inputs
    recipient_email = "etarneja@mba2026.hbs.edu"
    subject = "Harvard Students Researching Manufacturing Space (Automated)"
    body = """Hello Eshan,
I am a harvard student interested in studying the manufacturing space. I saw your profile and experience and thought you would be someone with a unique perspective.
Would you be willing to talk with me for 15 minutes?
Bill"""

    # Get sender's email
    sender_email = input("Enter your email address: ")

    # Confirm before creating draft
    print("\nDraft Email Details:")
    print(f"From: {sender_email}")
    print(f"To: {recipient_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body[:50]}..." if len(body) > 50 else f"Body: {body}")
    
    confirm = input("\nCreate this draft? (y/n): ").lower()
    if confirm == 'y':
        success = create_email_draft(subject, body, recipient_email, sender_email)
        if success:
            print("Draft created successfully! You can find it in the Email_Drafts folder in your home directory.")
        else:
            print("Failed to create draft. Please check your inputs and try again.")
    else:
        print("Draft creation cancelled.")

if __name__ == "__main__":
    main()
