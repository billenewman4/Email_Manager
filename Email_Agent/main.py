from email_agent import create_email_agent, draft_email
from secrets import get_secret
import requests
import json
from web_agent import tavily_search

# Function to get sample contact from Node.js server
def get_sample_contact():
    try:
        response = requests.get(get_secret("EMAIL_DRAFTER_URL") + "/sample-contact")
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred while fetching the sample contact: {e}")
        return None

# Example usage
if __name__ == "__main__":
    try:
        variables = ["sender", "receiver", "context", "tone"]
        template = "Draft a {tone} email from {sender} to {receiver} regarding {context}."
        
        email_agent = create_email_agent(variables, template)
        
        # Get sample contact
        sample_contact = get_sample_contact()
        if sample_contact:
            print("Sample Contact:")
            print(json.dumps(sample_contact, indent=2))
            
            # search web for context about the company and the person
            context = {}
            context['company_info'] = tavily_search(sample_contact['company'])
            context['person_info'] = tavily_search(sample_contact['name'])
            print(json.dumps(context, indent=2))


            # Use the sample contact data to draft an email
            draft = draft_email(email_agent, 
                                sender="Bill Newman", # need to update to user input name
                                receiver=sample_contact['name'],
                                context=f"Please write an email to reach out to {sample_contact['name']} at {sample_contact['company']} as a student reaching out to see if he/she would be willing to talk about his/her work with me.",
                                tone="professional",
                                example_email="Dear [Name],\n\nI hope this email finds you well. My name is [Your Name], and I'm a student at [Your University]. I came across your work at [Company] and was fascinated by [specific aspect of their work].\n\nI would be grateful for the opportunity to speak with you about your experiences and insights in the field. Would you be willing to spare 15-20 minutes for a brief call or video chat?\n\nThank you for your time and consideration.\n\nBest regards,\n[Your Name]",
                                additional_context=context,
                                instructions="Please use the provided example email as a general structure, but personalize it using the additional context about the person and their company. Ensure the email is concise, respectful, and demonstrates genuine interest in the recipient's work.")
            print("\nDraft Email:")
            print(draft)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
