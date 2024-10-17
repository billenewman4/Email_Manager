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
                                sender="Bill Newman", # need to upate to user input name
                                receiver=sample_contact['name'],
                                context=f"First draft to {sample_contact['name']} about {sample_contact['company']}",
                                tone="professional")
            print("\nDraft Email:")
            print(draft)
        else:
            print("Failed to get sample contact. Using default values.")
            draft = draft_email(email_agent, 
                                sender="John Doe", 
                                receiver="Jane Smith", 
                                context="project update",
                                tone="professional")
            print(draft)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
