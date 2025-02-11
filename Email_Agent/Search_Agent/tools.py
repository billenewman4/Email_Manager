from langchain_core.tools import Tool
from ..Tavily.tools import tavily_client

def get_search_tools(search_type: str) -> list:
    """Returns the appropriate search tools based on the search type."""
    
    if search_type == "tavily":
        def search_with_context(query: str) -> dict:
            """
            Search the web using Tavily and return both search results and raw context.
            Use this tool when you need to gather detailed information about a person, company, or topic.
            """
            try:
                print(f"\nDEBUG: Tavily Search")
                print(f"Query: {query}")
                
                # Get search results
                search_response = tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=5
                )
                
                results = search_response.get('results', [])
                raw_context = str(search_response)
                
                # Limit context size
                if len(raw_context) > 10000:
                    raw_context = raw_context[:10000] + "... [truncated]"
                
                print(f"Found {len(results)} results")
                return {
                    "results": results,
                    "raw_context": raw_context
                }
            except Exception as e:
                print(f"Error in search_with_context: {str(e)}")
                return {
                    "results": [],
                    "raw_context": f"Error occurred: {str(e)}"
                }
            
        def search_with_extraction(query: str) -> tuple:
            """
            Search the web using Tavily and extract relevant information.
            Use this tool when you need to extract specific content from search results.
            """
            try:
                print(f"Searching with query: {query}")
                
                # Get search results
                search_response = tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=5
                )
                
                results = search_response.get('results', [])
                
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
                return extracted_content, raw_context
                
            except Exception as e:
                print(f"Error in search_with_extraction: {str(e)}")
                return f"Error performing search: {str(e)}", ""
            
        return [
            Tool(
                name="search_with_context",
                description="Search the web for information about a person or company",
                func=search_with_context
            ),
            Tool(
                name="search_with_extraction",
                description="Search and extract specific content from web results",
                func=search_with_extraction
            )
        ]
        
    elif search_type == "google":
        # Add Google search specific tools here
        pass
        
    else:
        raise ValueError(f"Unsupported search type: {search_type}")
