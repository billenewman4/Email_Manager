from secrets import get_secret
from typing import Optional, Dict
import requests

# Get API key from environment variables
API_KEY = get_secret('OCEAN_API_KEY')
BASE_URL = 'https://api.ocean.io/v2'  # Updated to v2

def search_single_organization(
    industry: str,
    location: str = None,
    min_employees: int = None,
    max_employees: int = None
) -> Optional[Dict]:
    """
    Search for a single organization using Ocean.io API v2.
    """
    url = f"{BASE_URL}/search/companies?apiToken={API_KEY}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    params = {
        'size': 1,
        'companiesFilters': {
            'industries': {
                'mode': 'anyOf',
                'industries': ['Manufacturing']
            },
            'countries': ['us']
        }
    }
    
    try:
        response = requests.post(url, json=params, headers=headers)
        if response.status_code != 200:
            print(f"Ocean API error: {response.status_code} - {response.text}")
            return None
            
        data = response.json()
        companies = data.get('companies', [])  # Changed from 'hits' to 'companies'
        
        if companies and len(companies) > 0:
            # Extract the company data from the nested structure
            return companies[0].get('company', None)  # Added .get('company')
        return None
        
    except Exception as e:
        print(f"Error searching organization: {str(e)}")
        return None
# Hardcoded company data to save API credits
MOCK_COMPANY = {
    "domain": "microsoft.com",  # Changed to Microsoft
    "countries": ["us"],
    "primaryCountry": "us",
    "companySize": "100001-500000",
    "industries": ["Software", "Cloud Computing", "Technology"],
    "name": "Microsoft Corporation"
}

def search_single_person(
    company_domain: str,
    title: str = None,
    department: str = None,
    seniority: str = None,
    require_email: bool = False
) -> Optional[Dict]:
    """
    Search for a single person using Ocean.io API v2.
    
    Args:
        company_domain: Domain of the company to search
        title: Job title to filter by
        department: Department to filter by
        seniority: Seniority level to filter by
        require_email: If True, only return contacts with verified emails
    
    Valid seniorities: 'Owner', 'Founder', 'Board Member', 'C-Level', 'Partner', 
                      'VP', 'Head', 'Director', 'Manager', 'Other'
    """
    url = f"{BASE_URL}/search/people?apiToken={API_KEY}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    params = {
        'size': 1,
        'companiesFilters': {
            'includeDomains': [company_domain]
        },
        'peopleFilters': {}
    }
    
    # Add optional filters based on function inputs
    if require_email:
        params['peopleFilters']['emailStatuses'] = ['verified']
    
    if title:
        params['peopleFilters']['jobTitles'] = [title]
    
    if department:
        params['peopleFilters']['departments'] = [department]
        
    if seniority:
        params['peopleFilters']['seniorities'] = [seniority]
    
    try:
        print(f"Searching for person at domain: {company_domain}")
        print(f"With params: {params}")
        
        response = requests.post(url, json=params, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code != 200:
            print(f"Ocean API error: {response.status_code} - {response.text}")
            return None
            
        data = response.json()
        people = data.get('people', [])
        
        if people and len(people) > 0:
            return people[0].get('person', {})
        return None
        
    except Exception as e:
        print(f"Error searching person: {str(e)}")
        return None

def search_people_emails(
    company_domain: str,
    limit: int = 10,
    title: str = None,
    department: str = None,
    seniority: str = None,
    require_verified_email: bool = False
) -> list[dict]:
    """
    Search for multiple people and their emails using Ocean.io API v2.
    """
    url = f"{BASE_URL}/search/people?apiToken={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    params = {
        'size': limit,
        'companiesFilters': {
            'includeDomains': [company_domain]
        },
        'peopleFilters': {
            'emailStatuses': ['catchAll'] 
        }
    }
    
    # Add optional filters
    if title:
        params['peopleFilters']['jobTitles'] = [title]
    
    if department:
        params['peopleFilters']['departments'] = [department]
        
    if seniority:
        params['peopleFilters']['seniorities'] = [seniority]
    
    try:
        print(f"Searching for people at domain: {company_domain}")
        print(f"With params: {params}")
        
        response = requests.post(url, json=params, headers=headers)
        
        if response.status_code != 200:
            print(f"Ocean API error: {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        people = data.get('people', [])
        total = data.get('total', 0)
        
        print(f"\nFound {total} total matches")
        print(f"Returning first {len(people)} results")
        
        # Format the results using the actual response structure
        results = []
        for person in people:
            formatted_person = {
                'name': f"{person.get('firstName', '')} {person.get('lastName', '')}",
                'title': person.get('jobTitle', 'N/A'),
                'department': ', '.join(person.get('departments', [])),
                'seniority': ', '.join(person.get('seniorities', [])),
                'location': person.get('location', 'N/A'),
                'linkedin': person.get('linkedinUrl', 'N/A'),
                'summary': person.get('summary', ''),
                'email': person.get('email', {}).get('address', 'N/A'),
                'email_status': person.get('email', {}).get('status', 'N/A')
            }
            results.append(formatted_person)
        
        return results
        
    except Exception as e:
        print(f"Error searching people: {str(e)}")
        return []

def main():
    if not API_KEY:
        print("Error: OCEAN_API_KEY not found in environment variables")
        return
        
    try:
        # Use hardcoded company data
        org = MOCK_COMPANY
            
        print(f"\nUsing Company Data:")
        print(f"Name: {org.get('name', 'N/A')}")
        print(f"Domain: {org.get('domain', 'N/A')}")
        
        # Search for single person first
        print("\nSearching for contact...")
        #person = search_single_person(
        #    company_domain=org.get('domain')
        #)
        person = {
            "people": [{
                "id": "9943a40f0d77dfa8",
                "domain": "microsoft.com",
                "name": "Alex Iovine",
                "firstName": "Alex",
                "lastName": "Iovine",
                "country": "us",
                "location": "Los Angeles Metropolitan Area",
                "linkedinUrl": "https://www.linkedin.com/in/alexiovine",
                "seniorities": ["Founder", "C-Level"],
                "departments": ["Management", "Founder/Owner"],
                "photo": "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2",
                "jobTitle": "Co-Founder and CIO",
                "jobTitleEnglish": "Co-Founder and CIO",
                "summary": "As a seasoned leader, I'm deeply committed to creating meaningful change in both people's..."
            }],
            "searchAfter": "NoRgdADANABARAaTrAnCAHAFgjntrwCGANgKYAeMAlgPYBuVAdqXALpA",
            "detail": "OK",
            "total": 720
        }
        if person:
            print("\nFound Contact:")
            print(f"Name: {person.get('firstName', '')} {person.get('lastName', '')}")
            print(f"Title: {person.get('jobTitle', 'N/A')}")
            print(f"Location: {person.get('location', 'N/A')}")
            print(f"LinkedIn: {person.get('linkedinUrl', 'N/A')}")
            print(f"Departments: {', '.join(person.get('departments', []))}")
            print(f"Seniorities: {', '.join(person.get('seniorities', []))}")
            if person.get('summary'):
                print(f"Summary: {person.get('summary')}")
        else:
            print("No contact found")
            
        # Search for multiple people
        print("\nSearching for additional contacts...")
        people = search_people_emails(
            company_domain=org.get('domain'),
            limit=1
        )
        
        if people:
            print(f"\nFound {len(people)} Additional Contacts:")
            for person in people:
                print("\nContact Details:")
                print(f"Name: {person['name']}")
                print(f"Title: {person['title']}")
                print(f"Department: {person['department']}")
                print(f"Seniority: {person['seniority']}")
                print(f"Location: {person['location']}")
                print(f"LinkedIn: {person['linkedin']}")
        else:
            print("No additional contacts found")
            
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == '__main__':
    main()

