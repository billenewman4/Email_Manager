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
    except Exception as e:
        print(f"Error creating draft message: {str(e)}")
        return False

def main():
    print("Welcome to the Outlook Draft Creator!")
    
    # Get user inputs
    recipient_email = input("Enter recipient's email address: ")
    subject = input("Enter email subject: ")
    print("Enter email body (press Enter twice to finish):")
    body_lines = []
    while True:
        line = input()
        if line:
            body_lines.append(line)
        else:
            break
    body = "\n".join(body_lines)

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
