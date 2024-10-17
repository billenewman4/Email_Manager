import os
from secrets import get_secret
from tavily import TavilyClient

# Retrieve Tavily API key
tavily_api_key = get_secret("TAVILY_API_KEY")

if not tavily_api_key:
    raise ValueError("Failed to retrieve Tavily API key from Secret Manager")

# Initialize Tavily client
tavily_client = TavilyClient(api_key=tavily_api_key)

def tavily_search(query, search_depth="basic", max_results=2):
    """
    Perform a search using Tavily API.
    
    :param query: The search query string
    :param search_depth: 'basic' or 'advanced' (default: 'basic')
    :param max_results: Maximum number of results to return (default: 5)
    :return: List of search results
    """
    try:
        response = tavily_client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results
        )
        return response['results']
    except Exception as e:
        print(f"An error occurred during Tavily search: {str(e)}")
        return []
