import os
from dotenv import load_dotenv
import requests

def url_finder(company_name):
   # Get the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate up to the parent directory where .env is located
    parent_dir = os.path.dirname(current_dir)

    # Construct the path to the .env file
    dotenv_path = os.path.join(parent_dir, '.env')

    # Load the .env file
    load_dotenv(dotenv_path)

    # Now you can use os.getenv to get your API key
    api_key = os.getenv("SERPAPI_KEY")

    params = {
        "engine": "google",
        "q": company_name, 
        "api_key": api_key
    }

    response = requests.get('https://serpapi.com/search', params=params)
    data = response.json()


    # Check if 'organic_results' exists in the response
    if 'organic_results' in data:
        links = []
        for result in data['organic_results']:
            links.append(result['link'])
        return links
    else:
        print("No 'organic_results' found in the response.")
        print("Available keys in the response:", data.keys())
        return []
    # Check for error messages
    if 'error' in data:
        print("Error message:", data['error'])
        return []