from typing import Tuple
from ..web_agent import (
    tavily_search,
    tavily_context_search, 
    tavily_extract_content,
    tavily_search_extract
)

# Search tools for supervisor agent
async def search_contact_info(query: str) -> Tuple[str, str]:
    """
    Search for contact information using Tavily API.
    
    Args:
        query: Search query string
        
    Returns:
        Tuple containing:
        - Processed content from search results
        - Raw context from search
    """
    return await tavily_search_extract(query)

def get_context_info(query: str, max_tokens: int = 4000, **kwargs) -> str:
    """
    Get contextual information using Tavily API.
    
    Args:
        query: Search query string
        max_tokens: Maximum tokens for context
        **kwargs: Additional search parameters
        
    Returns:
        Context string for RAG applications
    """
    return tavily_context_search(query, max_tokens, **kwargs)

def extract_url_content(query: str, max_results: int = 2) -> dict:
    """
    Extract content from URLs found in search results.
    
    Args:
        query: Search query string
        max_results: Maximum number of search results
        
    Returns:
        Dictionary with extracted content and failed URLs
    """
    return tavily_extract_content(query, max_results)

def basic_search(query: str, **kwargs) -> Tuple[list, str]:
    """
    Perform basic search using Tavily API.
    
    Args:
        query: Search query string
        **kwargs: Additional search parameters
        
    Returns:
        Tuple containing:
        - List of search results
        - Raw context string
    """
    return tavily_search(query, **kwargs)
