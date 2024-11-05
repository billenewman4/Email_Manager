import os
from email_agent import EmailAgent
from secrets import get_secret
import requests
import json
from web_agent import tavily_context_search
import csv
from datetime import datetime
import asyncio
from typing import List
import aiohttp
from dataclasses import dataclass
from tavily import TavilyClient
from functools import partial

# adding new comment

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from contacts import Contact

def read_contacts_from_sheets(spreadsheet_id: str, range_name: str, limit: int = 100) -> List[Contact]:
    """
    Read contacts from Google Sheets and return as Contact objects.
    
    :param spreadsheet_id: The ID of the Google Sheet
    :param range_name: The range to read (e.g., 'Sheet1!A2:G100')
    :param limit: Maximum number of contacts to read
    :return: List of Contact objects
    """
    try:
        # Setup Google Sheets credentials
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-key.json'
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # Build the Google Sheets service
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        
        # Request data from Google Sheets
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print('No data found in sheet.')
            return []
            
        # Get headers from first row
        headers = values[0]
        
        # Convert rows to Contact objects
        contacts = []
        for row in values[1:limit+1]:  # Skip header row and respect limit
            # Pad row with empty strings if it's shorter than headers
            row_data = row + [''] * (len(headers) - len(row))
            
            # Create dictionary with header keys and row values
            contact_data = dict(zip(headers, row_data))
            
            # Create Contact object
            contact = Contact(contact_data)
            
            # Only add valid contacts
            if contact.is_valid_contact():
                contacts.append(contact)
        
        print(f"Successfully read {len(contacts)} contacts from Google Sheets")
        return contacts
        
    except Exception as e:
        print(f"Error reading from Google Sheets: {str(e)}")
        return []

def read_contacts_from_csv(file_path, limit=100):
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
               if row.get('Work Email') and row.get('Work Email').strip():
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

async def tavily_context_search(query: str) -> str:
    """
    Perform an async web search using Tavily API.
    """
    api_key = get_secret('TAVILY_API_KEY')
    client = TavilyClient(api_key=api_key)
    
    # Run the synchronous Tavily search in a thread pool
    loop = asyncio.get_running_loop()
    try:
        response = await loop.run_in_executor(
            None,
            partial(client.search, query=query, search_depth="advanced", max_results=5)
        )
        
        if response and 'results' in response:
            contents = [result.get('content', '') for result in response['results']]
            return ' '.join(contents)
        return ''
    except Exception as e:
        print(f"Error in Tavily search: {str(e)}")
        return ''

async def search_web(contact: dict) -> dict:
    """
    Perform web searches for company and person information concurrently.
    """
    try:
        # Create tasks for both searches
        if contact['company_domain']:
            company_query = f"site:{contact['company_domain']} {contact['company']}"
        else:
            company_query = contact['company']
        
        person_query = f"{contact['name']} {contact['job_title']} {contact['company']}"
        
        # Run both searches concurrently
        company_task = asyncio.create_task(tavily_context_search(company_query))
        person_task = asyncio.create_task(tavily_context_search(person_query))
        
        # Wait for both searches to complete
        company_info, person_info = await asyncio.gather(company_task, person_task)
        
        return {
            'company_info': company_info,
            'person_info': person_info
        }
    except Exception as e:
        print(f"Error in web search: {str(e)}")
        return {
            'company_info': '',
            'person_info': ''
        }

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

@dataclass
class EmailData:
    name: str
    email: str
    subject: str
    body: str
    timestamp: str

async def process_single_contact(contact: dict, email_agent: EmailAgent) -> EmailData | None:
    """
    Process a single contact asynchronously, completing all steps for one contact
    before moving to the next
    """
    try:
        print(f"\nStarting to process contact: {contact['name']}")
        
        # Search the web
        print(f"Searching web for: {contact['name']}")
        web_context = await search_web(contact)
        print(f"Web search complete for: {contact['name']}")

        # Immediately process this contact's context
        raw_context = (
            f"Name: {contact['name']}\n"
            f"Company: {contact['company']}\n"
            f"Job Title: {contact['job_title']}\n"
            f"LinkedIn: {contact['linkedin_profile']}\n"
            f"Company Domain: {contact['company_domain']}\n"
            f"Company Info: {web_context.get('company_info', '')}\n"
            f"Person Info: {web_context.get('person_info', '')}"
        )
        
        print(f"Extracting experiences for: {contact['name']}")
        experiences, email_body = await email_agent.process_contact(
            contact['name'],
            contact['company'],
            raw_context
        )
        print("email_body", email_body)

        print(f"\nProcessing complete for: {contact['name']}")
        print(f"Experiences extracted for: {contact['name']}")
        print(f"Email drafted for: {contact['name']}")
        print (f"Email: {email_body}")

        return EmailData(
            name=contact['name'],
            email=contact['email'],
            subject=f"Following up - {contact['company']}",
            body=email_body,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except Exception as e:
        print(f"Error processing contact {contact['name']}: {str(e)}")
        return None

def save_emails_to_csv(email_data_list: List[EmailData]):
    """
    Save multiple email details to a CSV file at once.
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
            
            # Write all email data at once
            for email_data in email_data_list:
                if email_data:  # Only write if email_data is not None
                    writer.writerow({
                        'Name': email_data.name,
                        'Email Address': email_data.email,
                        'Subject': email_data.subject,
                        'Email Body': email_data.body,
                        'Timestamp': email_data.timestamp
                    })
            
        print(f"All email details saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")

async def process_all_contacts(contacts: List[dict]):
    """
    Process contacts concurrently in smaller batches to manage API rate limits
    """
    email_agent = EmailAgent()
    results = []
    batch_size = 10  # Adjust this number based on API limits
    
    # Process contacts in batches
    for i in range(0, len(contacts), batch_size):
        batch = contacts[i:i + batch_size]
        print(f"\nProcessing batch of {len(batch)} contacts...")
        
        # Create tasks for the batch
        tasks = [
            asyncio.create_task(
                process_single_contact(contact, email_agent),
                name=f"Contact_{contact['name']}"  # Name the task for better tracking
            )
            for contact in batch
        ]
        
        # Wait for the current batch to complete
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(batch_results)
        
        # Print batch completion status
        successful = sum(1 for r in batch_results if isinstance(r, EmailData))
        print(f"Batch complete. Successful: {successful}/{len(batch)}")
    
    # Filter out None values and exceptions
    valid_results = [r for r in results if isinstance(r, EmailData)]
    failed = len(results) - len(valid_results)
    
    # Save all successful results to CSV at once
    if valid_results:
        save_emails_to_csv(valid_results)
    
    print(f"\nAll processing complete. Successful: {len(valid_results)}, Failed: {failed}")

if __name__ == "__main__":
    try:
        # Set up the file path to the CSV
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, 'data', 'contacts.csv')
        
        print(f"Attempting to read CSV from: {csv_file_path}")
        
        # Read all contacts from CSV
        contacts = read_contacts_from_csv(csv_file_path)
        
        if not contacts:
            raise ValueError("No contacts found in the CSV file")

        # Run the async processing
        asyncio.run(process_all_contacts(contacts))

    except Exception as e:
        print(f"An error occurred: {str(e)}")
