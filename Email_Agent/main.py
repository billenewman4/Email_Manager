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
from web_agent import tavily_search
from functools import partial
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from contacts import Contact

#GLobal variables
SPREADSHEET_ID = '1xyGHQBRn5dfFG3utdAifs2ubMJtolVK9Qoy9YJGoheg'
RANGE_NAME = 'Sheet1!A1:I'

def read_contacts_from_sheets(spreadsheet_id: str, range_name: str, limit: int = 400 ) -> List[Contact]:
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
        SERVICE_ACCOUNT_FILE = 'customeroutreach-440901-18943c7c0e95.json'
        
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
        
        # Define expected headers based on Contact object
        expected_headers = [
            'Match', 'Full Name', 'Job Title', 'Location', 
            'Company Domain', 'Company Name', 'LinkedIn', 
            'Work Email', 'draft_email'
        ]
        
        # Check if headers match expected headers
        if headers != expected_headers:
            raise ValueError(f"Header mismatch: Expected {expected_headers}, but got {headers}")
        
        # Convert rows to Contact objects
        contacts = []
        for row in values[1:limit+1]:  # Skip header row and respect limit
            # Pad the row with empty strings if needed
            padded_row = row + [''] * (len(headers) - len(row))
            
            # Create dictionary with header keys and row values
            row_data = dict(zip(headers, padded_row))
            
            # Debug print raw data
            print(f"\nRaw data for {row_data.get('Full Name')}:")
            print(f"Draft Email column raw value: '{row_data.get('draft_email')}'")
            print(f"Row data: {row_data}")
            
            # Create Contact object
            contact = Contact(row_data)
            
            # Debug print contact object
            print(f"Contact object draft_email: '{contact.draft_email}'")
            print(f"Is valid: {contact.is_valid_contact()}")
            
            # Only add valid contacts (validation happens in is_valid_contact())
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
                   'LinkedIn': row.get('LinkedIn Profile', ''),
                   'company': row.get('Company Name', '')
                }
               contacts.append(contact)
   except Exception as e:
       print(f"An error occurred while reading the CSV file: {e}")
   return contacts

async def search_web(contact: dict) -> dict:
    """
    Perform web searches for company and person information concurrently.
    """
    try:
        # Create tasks for both searches
        if contact['company_domain']:
            company_query = f"Tell me about {contact['company']} with website site:{contact['company_domain']} so I can get more context for a cold email"
        else:
            company_query = contact['company']
        
        person_query = f" Tell me about {contact['name']} who works at {contact['company']} as {contact['job_title']}"
        
        print("\n" + "="*50)
        print("Starting web searches:")
        print(f"Company query: {company_query}")
        print(f"Person query: {person_query}")
        print("="*50 + "\n")
        
        # Run both searches concurrently
        company_task = asyncio.create_task(tavily_search(company_query))
        person_task = asyncio.create_task(tavily_search(person_query))
        
        # Wait for both searches to complete
        company_info, person_info = await asyncio.gather(company_task, person_task)
        
        # Debug print the results
        print("\n" + "="*50)
        print("Search Results:")
        print(f"Company info found: {'Yes' if company_info else 'No'}")
        print(f"Company info length: {len(company_info) if company_info else 0}")
        print(f"Person info found: {'Yes' if person_info else 'No'}")
        print(f"Person info length: {len(person_info) if person_info else 0}")
        print("="*50 + "\n")
        
        return {
            'company_info': company_info or '',  # Ensure we return empty string if None
            'person_info': person_info or ''     # Ensure we return empty string if None
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

async def process_single_contact(contact: Contact, email_agent: EmailAgent) -> Contact:
    """
    Process a single contact asynchronously
    """
    try:
        if contact.draft_email:
            print(f"\nSkipping {contact.full_name} because they already have a draft email")
            return None
        if not contact.work_email:
            print(f"\nSkipping {contact.full_name} because they don't have a work email")
            return None
        
        print(f"\nStarting to process contact: {contact.full_name}")
        
        # Search the web
        web_context = await search_web({
            'name': contact.full_name,
            'company_domain': contact.company_domain,
            'job_title': contact.job_title,
            'LinkedIn': contact.LinkedIn,
            'company': contact.company_domain.split('.')[0] if contact.company_domain else ''
        })
        print(f"Web search complete")
        contact.context = str(web_context.get('company_info', '') + web_context.get('person_info', ''))
        print(f"Context: updated")


        # Process with email agent
        experiences, email_body = await email_agent.process_contact(
            contact,
        )
        
        # Debug printing
        print("\nProcessed Contact Information:")
        print(f"Name: {contact.full_name}")
        print(f" Context Length: {len(contact.context)}")
        print(f"Draft Email Length: {len(contact.draft_email) if contact.draft_email else 0}")

        return contact
        
    except Exception as e:
        print(f"Error processing contact {contact.full_name}: {str(e)}")
        return contact

def save_emails_to_csv(contacts: List[Contact]):
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
            for contact in contacts:
                if contact.work_email:  # Only write if email_data is not None
                    writer.writerow({
                        'Name': contact.full_name,
                        'Email Address': contact.work_email,
                        'Email Body': contact.draft_email,
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
        print(f"All email details saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")

async def process_all_contacts(contacts: List[Contact]):
    """
    Process contacts concurrently in smaller batches to manage API rate limits
    """
    # Filter invalid contacts BEFORE processing
    valid_contacts = [contact for contact in contacts if contact.is_valid_contact()]
    print(f"Filtered out {len(contacts) - len(valid_contacts)} contacts that didn't meet validation criteria")
    
    email_agent = EmailAgent()
    results = []
    batch_size = 10  # Adjust this number based on API limits
    
    # Process only valid contacts in batches
    for i in range(0, len(valid_contacts), batch_size):
        batch = valid_contacts[i:i + batch_size]
        print(f"\nProcessing batch of {len(batch)} contacts...")
        
        # Create tasks for the batch
        tasks = [
            asyncio.create_task(
                process_single_contact(contact, email_agent),
                name=f"Contact_{contact.full_name}"  # Changed from contact['name'] to contact.full_name
            )
            for contact in batch
        ]
        
        # Wait for the current batch to complete
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(batch_results)
        
        # Print batch completion status
        successful = sum(1 for r in batch_results if isinstance(r, Contact))
        print(f"Batch complete. Successful: {successful}/{len(batch)}")
    
    # Filter out None values and exceptions
    valid_results = [r for r in results if isinstance(r, Contact)]
    failed = len(results) - len(valid_results)
    
    print(f"\nAll processing complete. Successful: {len(valid_results)}, Failed: {failed}")
    return valid_results

def update_sheet_with_contact_info(spreadsheet_id: str, range_name: str, contacts: List[Contact]) -> None:
    """
    Update specific rows in Google Sheet with processed contact information.
    Only updates rows where we find a matching contact and only updates changed fields.
    """
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'customeroutreach-440901-18943c7c0e95.json'
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        
        # Get current sheet data once
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name  # Extended range to include all fields
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("No data found in sheet.")
            return
        
        # Get headers from the first row
        headers = values[0]
        
        # Create a mapping from header names to column indices
        header_to_index = {header: idx for idx, header in enumerate(headers)}
        
        # Create email to row index mapping to avoid repeated searches
        email_to_row = {}
        if len(values) > 1:  # If we have data rows
            for idx, row in enumerate(values[1:], start=2):  # Skip header
                if len(row) > header_to_index.get('Work Email', -1):  # Check if email column exists
                    email_to_row[row[header_to_index['Work Email']]] = idx
         
        # Prepare updates
        updates = []
        for contact in contacts:
            # Convert contact to row data
            new_row = contact.to_list()
            
            # Check if contact exists using our mapping
            if contact.work_email in email_to_row:
                row_idx = email_to_row[contact.work_email]
                print(f"Updating existing contact at row {row_idx}: {contact.full_name}")

                updates.append({
                    'range': f'Sheet1!A{row_idx}:{chr(65 + len(headers) - 1)}{row_idx}',
                    'values': [new_row]
                })
            else:
                next_row = len(values) + 1
                print(f"Adding new contact at row {next_row}: {contact.full_name}")
                updates.append({
                    'range': f'Sheet1!A{next_row}:{chr(65 + len(headers) - 1)}{next_row}',
                    'values': [new_row]
                })
                values.append(new_row)  # Simulate adding a new row
        
        # Execute updates
        if updates:
            body = {
                'valueInputOption': 'RAW',
                'data': updates
            }
            
            result = service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            print(f"Updated/Added {len(updates)} rows in the sheet")
            return result
        else:
            print("No updates needed")
            return None
            
    except Exception as e:
        print(f"Error updating Google Sheet: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

async def main():
    try:
        SPREADSHEET_ID = '1xyGHQBRn5dfFG3utdAifs2ubMJtolVK9Qoy9YJGoheg'
        
        # Read contacts
        contacts = read_contacts_from_sheets(SPREADSHEET_ID, RANGE_NAME)
        
        print("\nContacts loaded:")
        for i, contact in enumerate(contacts, 1):
            print(f"\nContact {i}:")
            print(f"Name: {contact.full_name}")
            print(f"Email: {contact.work_email}")
            print(f"Company: {contact.company_domain}")
            print(f"Job Title: {contact.job_title}")
            print(f"LinkedIn: {contact.LinkedIn}")
        
        if contacts:
            print("\nProcessing contacts...")
            # Wait for all contacts to be processed
            processed_contacts = await process_all_contacts(contacts)
            
            if processed_contacts:
                # Export to CSV
                print("\nExporting contacts to CSV...")
                save_emails_to_csv(processed_contacts)

                
                # Update Google Sheet
                print("\nUpdating Google Sheet...")
                update_sheet_with_contact_info(SPREADSHEET_ID, RANGE_NAME, processed_contacts)
                
                print("\nProcess complete! Updated contacts:")
                for contact in processed_contacts:
                    print(f"\nContact: {contact.full_name}")
                    print(f"Company Context Length: {len(contact.context) if contact.context else 0}")
                    print(f"Draft Email Length: {len(contact.draft_email) if contact.draft_email else 0}")
            else:
                print("No contacts were successfully processed")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    # Normal execution
    asyncio.run(main())
    