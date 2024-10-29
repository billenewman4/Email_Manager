import win32com.client as win32
import csv
from datetime import datetime
import os

def create_outlook_draft(subject, body, recipient_email, recipient_name=None):
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)  # 0 represents an email item
        mail.Subject = subject
        mail.Body = body
        mail.To = recipient_email
        
        mail.Save()  # This saves the email as a draft
        
        # Save to CSV after creating draft
        save_email_to_csv(recipient_name or "Not Provided", 
                         recipient_email, 
                         subject, 
                         body)
        
        print("Draft message created and saved to CSV successfully.")
        return True
    except Exception as e:
        print(f"Error creating draft message: {str(e)}")
        return False

def save_email_to_csv(name, email, subject, body):
    """
    Save email details to a CSV file.
    Creates a new file if it doesn't exist, otherwise appends to existing file.
    """
    # Create 'logs' directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create filename with current date
    filename = os.path.join(logs_dir, f'email_log_{datetime.now().strftime("%Y-%m-%d")}.csv')
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(filename)
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Name', 'Email Address', 'Subject', 'Email Body', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write headers if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the email data
            writer.writerow({
                'Name': name,
                'Email Address': email,
                'Subject': subject,
                'Email Body': body,
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
        print(f"Email details saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")

def main():
    print("Welcome to the Outlook Draft Creator!")
    
    # Get user inputs
    recipient_name = input("Enter recipient's name: ")
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
    print(f"To: {recipient_name} <{recipient_email}>")
    print(f"Subject: {subject}")
    print(f"Body: {body[:50]}..." if len(body) > 50 else f"Body: {body}")
    
    confirm = input("\nCreate this draft? (y/n): ").lower()
    if confirm == 'y':
        success = create_outlook_draft(subject, body, recipient_email, recipient_name)
        if success:
            print("Draft created successfully! You can find it in your Outlook Drafts folder.")
            print("Email details have been saved to the logs directory.")
        else:
            print("Failed to create draft. Please check your inputs and try again.")
    else:
        print("Draft creation cancelled.")

def view_email_log():
    """
    View the contents of today's email log.
    """
    filename = os.path.join('logs', f'email_log_{datetime.now().strftime("%Y-%m-%d")}.csv')
    
    if not os.path.exists(filename):
        print("No email log found for today.")
        return
    
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            print("\nToday's Email Log:")
            print("-" * 80)
            for row in reader:
                print(f"Name: {row['Name']}")
                print(f"Email: {row['Email Address']}")
                print(f"Subject: {row['Subject']}")
                print(f"Body: {row['Email Body'][:100]}...")  # Show first 100 chars of body
                print(f"Timestamp: {row['Timestamp']}")
                print("-" * 80)
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")

if __name__ == "__main__":
    while True:
        print("\nOutlook Draft Creator Menu:")
        print("1. Create new draft email")
        print("2. View today's email log")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            main()
        elif choice == '2':
            view_email_log()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
