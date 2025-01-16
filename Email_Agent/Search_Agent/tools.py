from langchain.agents import Tool
from ..web_agent import tavily_search_extract, tavily_search
import asyncio

def sync_tavily_search(query: str) -> str:
    """Synchronous wrapper for tavily search."""
    async def run_search():
        results, raw_context = await tavily_search(query)
        return results, raw_context

    try:
        results, raw_context = asyncio.run(run_search())
        return f"""
        SEARCH RESULTS:
        {results}
        
        ADDITIONAL CONTEXT:
        {raw_context}
        """
    except RuntimeError as e:
        # Handle case where event loop is already running
        loop = asyncio.get_event_loop()
        results, raw_context = loop.run_until_complete(run_search())
        return f"""
        SEARCH RESULTS:
        {results}
        
        ADDITIONAL CONTEXT:
        {raw_context}
        """

# Create tool instance
tavily_search_tool = Tool(
    name="tavily_search",
    func=sync_tavily_search,
    description="""
    Use this tool to search for information about people, companies, or topics.
    This tool performs an advanced web search and returns both detailed content and context.
    Best for: Finding professional information, company details, news, and recent updates.
    Input should be a specific search query.
    """
)
