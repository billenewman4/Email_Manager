from email_agent import EmailAgent
from contacts import Contact
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
    context['company_info'] = tavily_context_search(contact.company)
    context['person_info'] = tavily_context_search(contact.name)
    return context

if __name__ == "__main__":
    try:
        # Step 1: Get sample contact
        sample_contact_data = get_sample_contact()
        if not sample_contact_data:
            raise ValueError("Failed to get sample contact")
        print("Sample Contact:")
        print(json.dumps(sample_contact_data, indent=2))

        # Create Contact object
        contact = Contact(sample_contact_data)
        print("\nContact object created successfully")

        # Create EmailAgent
        email_agent = EmailAgent(contact)
        print("\nEmailAgent created successfully")

        # Step 2: Search the web
        web_context = search_web(contact)
        print("\nWeb Search Results:")
        print(json.dumps(web_context, indent=2))

        # Step 3: Extract relevant content and update context
        raw_context = web_context['company_info'] + "\n" + web_context['person_info']
        relevant_content = email_agent.extract_relevant_content(raw_context)
        print("\nRelevant Content Extracted:")
        print(relevant_content)

        email_agent.update_context("Web search results", relevant_content)
        print("\nContext updated successfully")

        # Step 4: Draft email
        print("\nStarting to draft email (main)...")
        email_agent.draft_email(
            tone="professional",
            new_context=f"reaching out as a student to discuss {contact.name}'s work at {contact.company}"
        )
        print("\nEmail drafted successfully", email_agent.latest_draft)

        # Step 5: Improve email
        print("\nStarting to improve email...")
        improved_draft = email_agent.improve_email()
        print("\nEmail improved successfully")

        # Optional: Print the current context
        print("\nCurrent Context:")
        print(email_agent.get_current_context())

    except Exception as e:
        print(f"An error occurred: {str(e)}")
