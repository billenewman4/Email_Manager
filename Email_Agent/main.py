from email_agent import create_email_agent, draft_email
from secrets import get_secret
import requests
import json
from web_agent import tavily_context_search
from relevant_content import create_relevant_content_extractor

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

def extract_relevant_content(extractor, raw_context, person_name, company_name):
    return extractor.invoke({
        "raw_context": raw_context,
        "person_name": person_name,
        "company_name": company_name
    })

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

        # Step 3: Extract relevant content
        content_extractor = create_relevant_content_extractor()
        relevant_content = extract_relevant_content(
            content_extractor,
            web_context['company_info'] + web_context['person_info'],
            sample_contact['name'],
            sample_contact['company']
        )
        print("\nRelevant Content:")
        print(relevant_content)

        # Step 4: Draft email
        variables = ["sender", "receiver", "context", "tone", "relevant_content"]
        template = "Draft a {tone} email from {sender} to {receiver} regarding {context}. Use this relevant information: {relevant_content}"
        email_agent = create_email_agent(variables, template)
        
        draft = draft_email(email_agent, 
                            sender="Bill Newman",  # need to update to user input name
                            receiver=sample_contact['name'],
                            context=f"reaching out as a student to discuss {sample_contact['name']}'s work at {sample_contact['company']}",
                            tone="professional",
                            relevant_content=relevant_content)
        
        print("\nDraft Email:")
        print(draft)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
