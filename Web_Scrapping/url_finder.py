import os
import requests
import sys
from secrets import get_secret

def url_finder(company_name):
    print(f"Starting url_finder for company: {company_name}", file=sys.stderr)

    # Get the API key using the get_secret function
    api_key = get_secret("SERPAPI_KEY")
    if api_key:
        print("API key loaded successfully", file=sys.stderr)
    else:
        print("ERROR: API key not found or is None", file=sys.stderr)
        return []

    params = {
        "engine": "google",
        "q": company_name, 
        "api_key": api_key
    }

    print("Sending request to SerpAPI", file=sys.stderr)
    response = requests.get('https://serpapi.com/search', params=params)
    print(f"Received response with status code: {response.status_code}", file=sys.stderr)

    data = response.json()
    print(f"Response data keys: {data.keys()}", file=sys.stderr)

    # Check if 'organic_results' exists in the response
    if 'organic_results' in data:
        links = []
        for result in data['organic_results']:
            links.append(result['link'])
        print(f"Found {len(links)} links", file=sys.stderr)
        return links
    else:
        print("No 'organic_results' found in the response.", file=sys.stderr)
        print("Available keys in the response:", data.keys(), file=sys.stderr)
        return []

    # Check for error messages
    if 'error' in data:
        print("Error message:", data['error'], file=sys.stderr)
        return []
