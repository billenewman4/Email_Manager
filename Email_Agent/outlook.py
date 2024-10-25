import win32com.client as win32

def create_outlook_draft(subject, body, recipient_email):
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)  # 0 represents an email item
        mail.Subject = subject
        mail.Body = body
        mail.To = recipient_email
        
        mail.Save()  # This saves the email as a draft
        print("Draft message created successfully.")
        return True
    except win32.pywintypes.com_error as e:
        print(f"COM Error: {str(e)}")
        print("Error details:")
        if e.excepinfo:
            print(f"  Error code: {e.excepinfo[5]}")
            print(f"  Error source: {e.excepinfo[2]}")
            print(f"  Error description: {e.excepinfo[1]}")
        else:
            print("  No additional error information available.")
        print("\nPossible reasons for this error:")
        print("1. Outlook is not installed on this system.")
        print("2. Outlook is not set as the default email client.")
        print("3. The script doesn't have permission to access Outlook.")
        print("4. There might be an issue with the Outlook installation.")
        print("\nTroubleshooting steps:")
        print("1. Ensure Microsoft Outlook is installed and properly set up.")
        print("2. Set Outlook as your default email application in Windows settings.")
        print("3. Try running the script with administrator privileges.")
        print("4. Repair or reinstall Microsoft Outlook if the issue persists.")
        return False
    except Exception as e:
        print(f"Unexpected error creating draft message: {str(e)}")
        return False

def main():
    print("Welcome to the Outlook Draft Creator!")
    
    # Use predefined inputs
    recipient_email = "etarneja@mba2026.hbs.edu"
    subject = "Harvard Students Researching Manufacturing Space (Automated)"
    body = """Hello Eshan,
I am a harvard student interested in studying the manufacturing space. I saw your profile and experience and thought you would be someone with a unique perspective.
Would you be willing to talk with me for 15 minutes?
Bill"""

    # Confirm before creating draft
    print("\nDraft Email Details:")
    print(f"To: {recipient_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body[:50]}..." if len(body) > 50 else f"Body: {body}")
    
    confirm = input("\nCreate this draft? (y/n): ").lower()
    if confirm == 'y':
        success = create_outlook_draft(subject, body, recipient_email)
        if success:
            print("Draft created successfully! You can find it in your Outlook Drafts folder.")
        else:
            print("Failed to create draft. Please check your inputs and try again.")
    else:
        print("Draft creation cancelled.")

if __name__ == "__main__":
    main()
