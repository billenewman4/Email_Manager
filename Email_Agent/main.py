import os
from email_agent import EmailAgent
from secrets import get_secret
import requests
import json
from web_agent import tavily_context_search
import csv

# def get_sample_contact():
#     try:
#         response = requests.get(get_secret("EMAIL_DRAFTER_URL") + "/sample-contact")
#         response.raise_for_status()
#         return response.json()
#     except requests.RequestException as e:
#         print(f"An error occurred while fetching the sample contact: {e}")
#         return None

def read_contacts_from_csv(file_path, limit=2):
    """
    Read contacts from a CSV file, up to a specified limit.
    
    :param file_path: Path to the CSV file
    :param limit: Maximum number of contacts to read (default: 2)
    :return: List of contact dictionaries
    """
    contacts = []
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                contact = {
                    'name': row.get('Full Name', ''),
                    'email': row.get('Work Email', ''),
                    'company_domain': row.get('Company Domain', ''),
                    'job_title': row.get('Job Title', ''),
                    'linkedin_profile': row.get('LinkedIn Profile', ''),
                    'company': row.get('Company Name', '')
                }
                contacts.append(contact)
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
    return contacts

def search_web(contact):
    """
    Perform web searches for company and person information.
    
    :param contact: Dictionary containing contact information
    :return: Dictionary with company and person information from web search
    """
    context = {}
    # Use company domain for more specific search if available
    if contact['company_domain']:
        company_query = f"site:{contact['company_domain']} {contact['company']}"
    else:
        company_query = contact['company']
    context['company_info'] = tavily_context_search(company_query)
    
    # Search for person information
    person_query = f"{contact['name']} {contact['job_title']} {contact['company']}"
    context['person_info'] = tavily_context_search(person_query)
    
    return context

if __name__ == "__main__":
    try:
        # Set up the file path to the CSV
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, 'data', 'contacts.csv')
        
        print(f"Attempting to read CSV from: {csv_file_path}")  # Debug print
        
        # Read contacts from CSV (limited to first two for testing)
        contacts = read_contacts_from_csv(csv_file_path, limit=2)
        
        if not contacts:
            raise ValueError("No contacts found in the CSV file")

        email_agent = EmailAgent()

        for contact in contacts:
            print(f"\nProcessing contact: {contact['name']}")
            print(json.dumps(contact, indent=2))

            # Search the web
            web_context = search_web(contact)
            print("\nWeb Search Results:")
            print(json.dumps(web_context, indent=2))

            # Process contact
            raw_context = (
                f"Name: {contact['name']}\n"
                f"Company: {contact['company']}\n"
                f"Job Title: {contact['job_title']}\n"
                f"LinkedIn: {contact['linkedin_profile']}\n"
                f"Company Domain: {contact['company_domain']}\n"
                f"Company Info: {web_context['company_info']}\n"
                f"Person Info: {web_context['person_info']}"
            )
            
            experiences, email = email_agent.process_contact(
                contact['name'],
                contact['company'],
                raw_context
            )

            print("\nExtracted Experiences:")
            print(experiences)

            print("\nDraft Email:")
            print(email)

        print("\nProcessing complete for the first two contacts.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
