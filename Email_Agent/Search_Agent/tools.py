from langchain_core.tools import tool
from ..Tavily.tools import tavily_search_extract, tavily_search

def get_search_tools(search_type: str) -> list:
    """Returns the appropriate search tools based on the search type."""
    
    if search_type == "tavily":
        @tool
        async def search_with_context(query: str) -> dict:
            """
            Search the web using Tavily and return both search results and raw context.
            
            Args:
                query (str): The search query to execute
                
            Returns:
                dict: Contains two keys:
                    - results: Summarized search results
                    - raw_context: Additional context from the search
            """
            results, raw_context = await tavily_search(query)
            return {
                "results": results,
                "raw_context": raw_context
            }
            
        @tool
        async def search_with_extraction(query: str) -> tuple:
            """
            Search the web using Tavily and extract relevant information.
            
            Args:
                query (str): The search query to execute
                
            Returns:
                tuple: (content, raw_context) where:
                    - content: Extracted and processed content
                    - raw_context: Raw search results for additional context
            """
            return await tavily_search_extract(query)
            
        return [search_with_context, search_with_extraction]
        
    elif search_type == "google":
        # Add Google search specific tools here
        pass
        
    else:
        raise ValueError(f"Unsupported search type: {search_type}")
