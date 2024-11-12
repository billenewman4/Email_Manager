import os
import json
from secrets_ret import get_secret
from tavily import TavilyClient

# Retrieve Tavily API key
tavily_api_key = get_secret("TAVILY_API_KEY")

if not tavily_api_key:
    raise ValueError("Failed to retrieve Tavily API key from Secret Manager")

# Initialize Tavily client
tavily_client = TavilyClient(api_key=tavily_api_key)

def tavily_search(query, search_depth="basic", max_results=1):
    """
    Perform a search using Tavily API.
    
    :param query: The search query string
    :param search_depth: 'basic' or 'advanced' (default: 'basic')
    :param max_results: Maximum number of results to return (default: 1)
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

def tavily_context_search(query, max_tokens=4000, **kwargs):
    """
    Perform a context search using Tavily API.
    
    :param query: The search query string
    :param max_tokens: Maximum number of tokens for the context (default: 40000)
    :param kwargs: Additional keyword arguments for the search
    :return: Context string for RAG applications
    """
    try:
        context = tavily_client.get_search_context(
            query=query,
            max_tokens=max_tokens,
            **kwargs
        )
        return context
    except Exception as e:
        print(f"An error occurred during Tavily context search: {str(e)}")
        return None

def tavily_extract_content(query, max_results=2):
    """
    Extract content from URLs found in Tavily search results.
    
    :param query: The search query string
    :param max_results: Maximum number of search results to use for extraction
    :return: Dictionary containing extracted results and failed URLs
    """
    try:
        # First, perform a search to get the URLs
        search_results = tavily_search(query, max_results=max_results)
        urls = [result['url'] for result in search_results]
        
        # Then, extract content from these URLs
        response = tavily_client.extract(urls=urls)
        print("Extracted content:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        return response
    except Exception as e:
        print(f"An error occurred during Tavily content extraction: {str(e)}")
        return None
