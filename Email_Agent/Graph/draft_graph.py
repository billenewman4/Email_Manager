from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.types import Command
import operator
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
import logging
from langchain.chat_models import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.ERROR)  # Only show ERROR and CRITICAL
for logger_name in [
    'Email_Agent.web_agent',
    'Email_Agent.secrets_ret',
    'google.auth.transport.requests',
    'urllib3.connectionpool',
    'google',
    'httpcore',
    'httpx',
]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

# Local imports
from ..tools.secrets_ret import get_secret
from ..Search_Agent.tools import tavily_search_tool
from ..Object_Classes.contacts import Contact
from ..Object_Classes.sender import Sender
from ..Drafting_Agent.agent import DraftingAgent
from ..Search_Agent.agent import SearchAgent
from ..Supervisor_agent.agent import SupervisorAgent

class EmailState(TypedDict):
    """State for the email drafting graph."""
    input: str
    workers_called: Annotated[List[str], operator.add] 
    messages: List[BaseMessage]
    contact: Contact
    sender: Sender
    draft: str
    draft_index: int
    search_index: int
    search_results: str
    summarized_search_results: Annotated[str, operator.add]
    AgentCommands: Command

def create_email_graph():
    openai_key = get_secret("OpenAPI_KEY")
    # Create system message for search agent
    system_message = """You are an AI assistant that searches for information about people, companies, or topics.
    This tool performs an advanced web search and returns both detailed content and context.
    Best for: Finding professional information, company details, news, and recent updates.
    Input should be a specific search query."""
    
    # Initialize search agent with required arguments
    search_agent = SearchAgent(
        openai_api_key=openai_key,
        tools=[tavily_search_tool],
        worker_name="search_agent",
        system_message=system_message
    )
    supervisor_agent = SupervisorAgent(openai_api_key=openai_key) 
    
    drafting_agent = DraftingAgent(
        openai_api_key=openai_key,
        worker_name="drafting_agent",
    )
    
    # Initialize graph
    builder = StateGraph(EmailState)
    
    # Add nodes
    builder.add_node("Supervisor", supervisor_agent.evaluate_email)
    builder.add_node("Search", search_agent.create_search_graph)
    builder.add_node("Draft", drafting_agent.draft_email)
    
    # Add edges with conditional routing
    builder.add_edge(START, "Search")
    builder.add_edge("Search", "Supervisor")
    
    # Edges from Supervisor with conditions
    builder.add_conditional_edges(
        "Supervisor",
        lambda x: x["AgentCommands"],
        {
            "SEARCH": "Search",
            "REDRAFT": "Draft",
            "END": END
        }
    )
    
    # Route back to Supervisor from Search and Draft
    builder.add_edge("Search", "Supervisor")
    builder.add_edge("Draft", "Supervisor")
    return builder.compile()


if __name__ == "__main__":
    # Get API key
    openai_key = get_secret("OpenAPI_KEY")
    
    # Create test contact with rich information
    test_contact = Contact({
        "Full Name": "Ben Kortlang",
        "Job Title": "Partner",
        "Company Name": "G2 Venture Partners",
        "Company Description": "N/A",
        "Location": "San Francisco, CA",
        "Department": "N/A",
        "LinkedIn": "N/A"
    })
    
    # Create test sender with detailed background
    test_sender = Sender(
        name="Alex Rivera",
        resume="""Computer Science and Business Analytics student at Stanford University
        - Research Assistant in NLP Lab working on large language models
        - Summer internship at DataTech focusing on ML model deployment
        - Led university's AI/ML student organization
        - Proficient in Python, PyTorch, and MLOps practices""",
        career_interest="AI/ML Venture Capital Investments",
        key_accomplishments=[
            "Published paper on efficient transformer architectures",
            "Built and deployed ML pipeline serving 10k+ users",
            "Winner of University Innovation Challenge"
        ],
        llm=ChatOpenAI(temperature=0.7, model="gpt-4-0125-preview", openai_api_key=openai_key)
    )
    
    # Initialize the graph with agents
    graph = create_email_graph()
    
    # Create comprehensive initial state
    initial_state = {
        "input": "Draft an email to connect about AI/ML Venture Capital Investments especially in enterprise AI solutions",
        "workers_called": [],
        "messages": [],
        "contact": test_contact,
        "sender": test_sender,
        "draft": "",
        "draft_index": 0,
        "search_index": 0,
        "search_results": "",
        "AgentCommands": None
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    # Print detailed results
    print("\n" + "="*50 + " GRAPH EXECUTION RESULTS " + "="*50)
    print(f"\nInput Query: {result['input']}")
    print(f"\nWorkers Called (Order of Operations): {result['workers_called']}")
    print(f"\nSearch Results: {result['search_results']}")
    print(f"\nFinal Draft: {result['draft']}")
    print(f"\nDraft Iterations: {result['draft_index']}")
    print(f"\nSearch Iterations: {result['search_index']}")
    print("\nMessage History:")
    for msg in result['messages']:
        print(f"\n{msg.type}: {msg.content[:200]}...")
    print("\n" + "="*120)
