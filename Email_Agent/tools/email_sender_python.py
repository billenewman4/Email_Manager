import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from typing import Dict, Optional, List, Union
import csv
from io import StringIO

# Use secrets module from the same directory
from Email_Agent.Tools.secrets_ret import get_secret

class EmailSender:
    def __init__(self):
        """Initialize the email sender with Gmail SMTP settings"""
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = get_secret("EMAIL_USER")
        # Get password from environment variable
        self.password = get_secret("EMAIL_PASS")
        
        if not self.password:
            raise ValueError("GMAIL_APP_PASSWORD environment variable not set")

    def create_message(self, 
                      to_email: str, 
                      subject: str, 
                      body: str,
                      attachments: Optional[List[Dict[str, Union[str, bytes]]]] = None) -> MIMEMultipart:
        """Create a MIME message with both HTML and plain text versions"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = to_email

        # Create plain text version
        text_part = MIMEText(body, "plain")
        
        # Create HTML version (convert newlines to <br>)
        html_body = body.replace("\n", "<br>")
        html_part = MIMEText(html_body, "html")

        # Attach both versions
        message.attach(text_part)
        message.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                part = MIMEApplication(
                    attachment['content'],
                    Name=attachment['filename']
                )
                part['Content-Disposition'] = f'attachment; filename="{attachment["filename"]}"'
                message.attach(part)

        return message

    def send_email(self, 
                  to_email: str, 
                  body: str, 
                  subject: Optional[str] = "Your Networking email is ready!",
                  attachments: Optional[List[Dict[str, Union[str, bytes]]]] = None) -> Dict:
        """
        Send an email using Gmail SMTP
        
        Args:
            to_email (str): Recipient's email address
            body (str): Email body content
            subject (str, optional): Email subject line
            
        Returns:
            dict: Response indicating success or failure
        """
        try:
            # Create SMTP session
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                # Enable TLS for security
                server.starttls()
                
                # Login to the server
                server.login(self.sender_email, self.password)
                
                # Create message
                message = self.create_message(to_email, subject, body, attachments)
                
                # Send email
                server.send_message(message)
                
                return {
                    "success": True,
                    "message": "Email sent successfully",
                    "to": to_email
                }

        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "to": to_email
            }

def send_email(email_body: str, email_address: str, csv_data: Optional[List[Dict]] = None) -> Dict:
    """
    Wrapper function to maintain compatibility with existing code
    
    Args:
        email_body (str): The body text of the email
        email_address (str): Recipient's email address
        csv_data: Parameter maintained for backwards compatibility but no longer used
        
    Returns:
        dict: Response indicating success or failure
    """
    try:
        sender = EmailSender()
        # No longer using attachments
        return sender.send_email(email_address, email_body, attachments=None)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "to": email_address
        }

def test_email_service():
    """Test function to verify email functionality"""
    test_body = """
    Hello!
    
    This is a test email sent from the email_sender_python.py script.
    
    Best regards,
    Email Agent
    """
    test_address = "billenewman4@gmail.com"  # Using your actual email from .env
    
    print("\n=== Testing Email Service ===")
    print(f"Sending test email to: {test_address}")
    result = send_email(test_body, test_address)
    
    if result.get("success"):
        print("✅ Email sent successfully!")
    else:
        print("❌ Failed to send email!")
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    test_email_service() 