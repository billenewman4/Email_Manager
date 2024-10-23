from email_agent import EmailAgent
from secrets import get_secret
import requests
import json
from web_agent import tavily_context_search

def get_sample_contact():
    try:
        response = requests.get(get_secret("EMAIL_DRAFTER_URL") + "/sample-contact")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred while fetching the sample contact: {e}")
        return None

def search_web(contact):
    context = {}
    context['company_info'] = tavily_context_search(contact['company'])
    context['person_info'] = tavily_context_search(contact['name'])
    return context

if __name__ == "__main__":
    try:
        # Step 1: Get sample contact
        sample_contact = get_sample_contact()
        if not sample_contact:
            raise ValueError("Failed to get sample contact")
        print("Sample Contact:")
        print(json.dumps(sample_contact, indent=2))

        # Step 2: Search the web
        web_context = search_web(sample_contact)
        print("\nWeb Search Results:")
        print(json.dumps(web_context, indent=2))

        # Step 3: Create EmailAgent and process contact
        email_agent = EmailAgent()
        raw_context = web_context['company_info'] + web_context['person_info']
        experiences, email = email_agent.process_contact(
            sample_contact['name'],
            sample_contact['company'],
            raw_context
        )

        print("\nExtracted Experiences:")
        print(experiences)

        print("\nDraft Email:")
        print(email)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
