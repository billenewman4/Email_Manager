import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from ..Tools.secrets_ret import get_secret
import ssl
import certifi
import os
import platform

def get_ssl_context():
    """
    Create an SSL context that works across different platforms.
    On macOS, it will use the system certificates if available.
    """
    context = ssl.create_default_context(cafile=certifi.where())
    
    # On macOS, try to use the system certificates
    if platform.system() == 'Darwin':  # macOS
        try:
            import subprocess
            # Get the path to the macOS certificates
            cert_path = subprocess.check_output(
                ["security", "find-certificate", "-a", "-p", "/System/Library/Keychains/SystemRootCertificates.keychain"],
                text=True
            )
            if cert_path:
                context = ssl.create_default_context()
                context.load_verify_locations(cadata=cert_path)
        except Exception:
            # If there's any error, fall back to certifi
            pass
    
    return context

def send_email(
    to_email: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587
) -> dict:
    """
    Send an email using SMTP with TLS security.
    
    Args:
        to_email (str): Recipient's email address
        subject (str): Email subject
        body (str): Email body content (HTML or plain text)
        from_email (Optional[str]): Sender's email address. If None, uses EMAIL_ADDRESS from secrets
        smtp_server (str): SMTP server address (default: smtp.gmail.com)
        smtp_port (int): SMTP server port (default: 587 for TLS)
    
    Returns:
        dict: Response containing success status and message
    """
    try:
        # Get credentials from secrets
        email_address = from_email or get_secret("EMAIL_USER")
        email_password = get_secret("EMAIL_PASS")
        
        if not email_address or not email_password:
            return {
                "success": False,
                "message": "Failed to retrieve email credentials from secrets"
            }

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(body, 'html'))

        # Get the appropriate SSL context
        context = get_ssl_context()

        # Connect to SMTP server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()  # Identify ourselves to the server
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Re-identify ourselves over TLS connection
            server.login(email_address, email_password)
            server.send_message(msg)

        return {
            "success": True,
            "message": f"Email sent successfully to {to_email}"
        }

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": "Failed to authenticate with SMTP server. Please check your credentials."
        }
    except ssl.SSLError as e:
        return {
            "success": False,
            "message": f"SSL Certificate verification failed: {str(e)}"
        }
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "message": f"SMTP error occurred: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"An unexpected error occurred: {str(e)}"
        }

def test_email_connection() -> dict:
    """
    Test the email connection and credentials without sending an actual email.
    
    Returns:
        dict: Response containing success status and message
    """
    try:
        # Get credentials from secrets
        email_address = get_secret("EMAIL_USER")
        email_password = get_secret("EMAIL_PASS")
        
        if not email_address or not email_password:
            return {
                "success": False,
                "message": "Failed to retrieve email credentials from secrets"
            }

        # Get the appropriate SSL context
        context = get_ssl_context()

        # Test connection to SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()  # Identify ourselves to the server
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Re-identify ourselves over TLS connection
            server.login(email_address, email_password)

        return {
            "success": True,
            "message": "Email connection test successful"
        }

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": "Failed to authenticate with SMTP server. Please check your credentials."
        }
    except ssl.SSLError as e:
        return {
            "success": False,
            "message": f"SSL Certificate verification failed: {str(e)}"
        }
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "message": f"SMTP error occurred: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"An unexpected error occurred: {str(e)}"
        }

if __name__ == "__main__":
    # Test the email connection
    test_result = test_email_connection()
    print("Email Connection Test:", test_result)

    # Example usage of send_email function
    if test_result["success"]:
        result = send_email(
            to_email="test@example.com",
            subject="Test Email",
            body="<h1>This is a test email</h1><p>Hello from the Email Manager!</p>"
        )
        print("Send Email Result:", result)
