import requests
import json

def send_email(email_body: str) -> dict:
    """
    Sends an email with the given body text to a hardcoded email address.
    
    Args:
        email_body (str): The body text of the email to be sent
        
    Returns:
        dict: The response from the API call
    """
    # Create the email payload
    email_data = {
        "subject": "Your Networking email is ready!",
        "email": "eshantarneja@gmail.com",
        "body": email_body
    }
    
    # API endpoint
    url = "https://nylas-app-221518599345.us-central1.run.app/nylas/send-email-manager"

    
    
    # Headers for the request
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Make the POST request
        response = requests.post(
            url=url,
            headers=headers,
            json=email_data
        )
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Return the response as a dictionary
        return response.json()
        
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        print(f"Error sending email: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Test the send_email function
    test_body = "This is a test email sent from the email.py script!"
    print("Sending test email...")
    
    result = send_email(test_body)
    
    if "error" in result:
        print("Failed to send email!")
        print(f"Error: {result['error']}")
    else:
        print("Email sent successfully!")
        print("API Response:", result) 