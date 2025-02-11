import sys
from ..Tools.secrets_ret import get_secret
from tavily import TavilyClient

tavily_api_key = get_secret("TAVILY_API_KEY")

if not tavily_api_key:
    raise ValueError("Failed to retrieve Tavily API key from Secret Manager")

# Initialize Tavily client
tavily_client = TavilyClient(api_key=tavily_api_key)

def tavily_search(query: str, search_depth="advanced", max_results=5, include_raw_content=True):
    """
    Perform a search using Tavily API and get both search results and raw context.
    """
    try:
        print(f"\nDEBUG: Tavily Search")
        print(f"API Key: {tavily_api_key[:5]}...")
        print(f"Query: {query}")
        print(f"Search depth: {search_depth}")
        print(f"Max results: {max_results}")
        
        # Get search results
        search_response = tavily_client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_raw_content=include_raw_content,
            exclude_domains=[
                "mapquest.com",
                "facebook.com",
                "instagram.com", 
                "twitter.com"
            ]
        )
        
        results = search_response.get('results', [])
        
        # Limit raw context size to prevent token overflow
        raw_context = str(search_response)
        if len(raw_context) > 10000:  # Limit to ~2500 tokens
            raw_context = raw_context[:10000] + "... [truncated]"
        
        print(f"\nSearch completed successfully")
        print(f"Found {len(results)} results")
        print(f"Raw context length (after truncation): {len(raw_context)}")
        
        return results, raw_context
        
    except Exception as e:
        print(f"\nDEBUG: Tavily Search Error")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        return [], ""

def tavily_context_search(query: str, max_tokens=4000, **kwargs):
    """
    Perform a context search using Tavily API.
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

def tavily_search_extract(query: str) -> tuple[str, str]:
    """
    Perform a search using Tavily API and extract both content and raw context.
    """
    try:
        print(f"Searching with query: {query}")
        
        # Get regular search results
        results, _ = tavily_search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_raw_content=True
        )
        
        # Get raw context
        raw_context = tavily_client.get_search_context(
            query=query,
            max_tokens=4000,
            search_depth="advanced"
        )
        
        if not results:
            return "No search results found.", raw_context or ""
            
        # Extract and combine relevant content
        content = []
        for result in results:
            content.append(result.get('content', ''))
        
        extracted_content = ' '.join(content)
        
        print(f"Extracted content length: {len(extracted_content)}")
        print(f"Raw context length: {len(raw_context) if raw_context else 0}")
        
        return extracted_content, raw_context
        
    except Exception as e:
        print(f"Error in tavily_search_extract: {str(e)}")
        return f"Error performing search: {str(e)}", ""

if __name__ == "__main__":
    test_domain = "prccopack.com"
    print("\n" + "="*50)
    print("Testing Tavily functions with:", test_domain)
    print("="*50)

    # Test 1: Basic Search
    print("\n1. Testing tavily_search with different parameters:")
    print("-"*30)
    search_results, raw_context = tavily_search(
        query=f"Tell me about {test_domain}",
        search_depth="advanced",
        max_results=3
    )
    
    print("\nResults:")
    if search_results:
        for result in search_results:
            print(f"\nURL: {result.get('url')}")
            print(f"Content: {result.get('content', '')}...\n")
            print(f"Raw Content: {result.get('raw_content', '')}...\n")
    else:
        print("No results found")

    # Test 2: Context Search
    print("\n2. Testing tavily_context_search:")
    print("-"*30)
    context = tavily_context_search(
        query=f"What does {test_domain} company do? Their products and services?",
        max_tokens=4000,
        search_depth="advanced"
    )
    print("Context Results:", context)

    # Test 3: Content Extraction
    print("\n3. Testing tavily_extract_content:")
    print("-"*30)
    content, context = tavily_search_extract(
        query=f"Information about {test_domain}"
    )
    print("Extracted Content:", content[:200] + "..." if content else "None")
    print("Context Length:", len(context) if context else 0)
