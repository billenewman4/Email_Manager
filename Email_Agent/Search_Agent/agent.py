"""State for the email drafting graph."""
# standard imports
from typing import Annotated, List, TypedDict
import operator

# langchain imports
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from langgraph.constants import START, END

# local imports
from ..Tools.secrets_ret import get_secret
from ..Object_Classes.contacts import Contact
from ..Object_Classes.sender import Sender
from ..Search_Agent.tools import get_search_tools
from ..Search_Agent.prompts import get_prompt



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
    search_results: Annotated[str, operator.add]
    AgentCommands: Command

class SearchState(TypedDict):
    input: str
    workers_called: Annotated[List[str], operator.add]
    messages: List[BaseMessage] 
    contact: Contact
    sender: Sender
    draft: str
    search_index: int
    search_query: Annotated[str, operator.add]
    raw_search_results: str
    search_summary: Annotated[str, operator.add]
    AgentCommands: Command
    analysis_result: str

class SearchAgent:
    def __init__(self, worker_name: str, user_type: str):
        print("Initializing SearchAgent...")
        self.llm = ChatOpenAI(
            temperature=0.7,
            openai_api_key=get_secret("OpenAPI_KEY"), 
            model="gpt-4o-mini-2024-07-18"
        )
        self.tools = get_search_tools("tavily")
        self.worker_name = worker_name
        self.system_message = get_prompt(user_type)
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            state_modifier=self.system_message,
            debug=True
        )
        print(f"Search agent initialized with {self.worker_name}")
    
    def summarize_search(self, state: SearchState) -> SearchState:
        print("="*100)
        print("Summarizing search results...")
        print("="*100)

        # Safely get sender and contact info with defaults
        sender_name = getattr(state.get("sender", {}), "name", "User")
        contact_name = getattr(state.get("contact", {}), "full_name", "Contact")
        company_name = getattr(state.get("contact", {}), "company_name", "Company")
        search_results = state["raw_search_results"]

        summary_chain = (
            PromptTemplate(
                input_variables=["sender_name", "contact_name", "company_name", "search_results"],
                template="""Summarize the following search results in a professional context:
                
                CONTACT INFORMATION:
                - Name: {contact_name}
                - Company: {company_name}
                
                SEARCH RESULTS:
                {search_results}
                
                Please analyze these search results and extract information that would be relevant for {sender_name} 
                to reference when reaching out to {contact_name}.
                Focus on finding specific details, projects, or experiences that could create meaningful talking points.
                """
            ) 
            | self.llm 
            | StrOutputParser()
        )
        
        summary = summary_chain.invoke({
            "sender_name": sender_name,
            "contact_name": contact_name,
            "company_name": company_name,
            "search_results": search_results
        })

        print("\n\n\n\n\n\n\n\n\n") 
        print("="*100)
        print(f"Summary results: {summary}")
        print("="*100)
        print("\n\n\n\n\n\n\n\n\n")

        return {
            "workers_called": ["summarize_search"],
            "search_results": " ",
            "search_summary": summary
        }

    def search_context(self, state: EmailState) -> EmailState:
        print("="*100)
        print("Searching for context...")
        print("="*100)
        # Create the agent's input
        agent_input = ""
        if state.get("analysis_result"):
            agent_input = f"""
            Search for information about {state['contact'].full_name} at {state['contact'].company_name}.
            The feedback from the previous search attempt was: {state['analysis_result']}

            Use the tavily_search tool to find this information. Please do not repeat the same search query. Please use the feedback you recivied to improve your search query. Please only make one call to the tavily_search tool.
        
            Previous search attempt #{state['search_query']}
            """
        else:
            agent_input = f"""
            Search for information about {state['contact'].full_name} at {state['contact'].company_name}.
            Specifically looking for: {state['input']}
        
        
             Use the tavily_search tool to find this information. Please do not repeat the same search query. Please only make one call to the tavily_search tool.
            """
        

        print("="*100)
        print(f"Agent input: {agent_input}")
        print("="*100)
        print("\n\n\n\n\n\n\n\n\n")
        # Use the React agent to perform the search
        agent_response = self.agent.invoke({
            "messages": agent_input
        })
        
        # Extract the search results and query from the agent's response
        search_results = ""
        search_query = ""
        for message in agent_response["messages"]:
            if isinstance(message, ToolMessage):
                search_results = message.content
            elif isinstance(message, AIMessage) and message.additional_kwargs.get("tool_calls"):
                # Extract the actual search query used
                tool_call = message.additional_kwargs["tool_calls"][0]
                if tool_call["function"]["name"] == "tavily_search":
                    import json
                    args = json.loads(tool_call["function"]["arguments"])
                    search_query = args.get("query", "")

        print("="*100)
        print(f"Search query: {search_query}")
        print(f"Search results: {search_results[:200]}...")
        print("="*100)
        
        # Update and return state with latest results
        return {
            "workers_called": [self.worker_name],
            "messages": state["messages"] + [HumanMessage(content=search_results)],
            "search_index": state["search_index"] + 1,
            "search_query": search_query,  # Add the actual query used
            "raw_search_results": search_results  # Add the results received
        }
    
    def analyze_search(self, state: SearchState) -> SearchState:
        print("="*100)
        print("Analyzing search results...")
        print("="*100)

        analysis_prompt = """Analyze the following search results to determine if they contain the requested information:
        
        Search Query: {query}
        Search Results: {results}
        
        Does this contain sufficient information about {topic}? Respond with:
        SUFFICIENT: [Yes/No]
        REASON: [Brief explanation why]
        KEY_POINTS:
        - [Key point 1]
        - [Key point 2]
        - [Key point 3]
        """
        
        analysis_chain = PromptTemplate(
            input_variables=["query", "results", "topic"],
            template=analysis_prompt
        ) | self.llm | StrOutputParser()
        
        analysis_result = analysis_chain.invoke({
            "query": state["search_query"],
            "results": state["search_summary"],
            "topic": state["input"]
        })

        
        print("\n\n\n\n\n\n\n\n\n")
        print("="*100)
        print(f"Analysis result: {analysis_result}")
        print("="*100)
        print("\n\n\n\n\n\n\n\n\n")

        return {
            "workers_called": ["analyze search"],
            "analysis_result": analysis_result  # Store the analysis result in state
        }

    def create_search_graph(self, state: EmailState) -> EmailState:
        # Get API key
        openai_key = get_secret("OpenAPI_KEY")
        print("="*100)
        print(f"Creating search graph!")
        print("="*100)
        

        # Create graph with initial SearchState
        builder = StateGraph(SearchState)
        
        # Initialize SearchState from EmailState
        initial_state = {
            "input": state["input"],
            "workers_called": [],
            "messages": state["messages"],
            "contact": state["contact"],
            "sender": state["sender"],
            "draft": state["draft"],
            "search_index": 0,
            "search_query": "",
            "search_results": "",
            "search_summary": "",
            "AgentCommands": None,
            "analysis_result": ""
        }
        
        # Create nodes and edges
        builder.add_node("Search", self.search_context)
        builder.add_node("Summarize", self.summarize_search)
        builder.add_node("Analysis", self.analyze_search)
        
        # Add edges
        builder.add_edge(START, "Search")
        builder.add_edge("Search", "Summarize")
        builder.add_edge("Summarize", "Analysis")
        
        def should_continue(state):
            print("="*100)
            print ("Should continue?")
            print("="*100)
            print("state workers called: ", state["workers_called"])
            print("="*100)
            print("state messages: ", state["messages"])
            print("="*100)
            print("state search index: ", state["search_index"])
            print("="*100)
            print("state search query: ", state["search_query"])
            print("="*100)
            print("state search summary: ", state["search_summary"])
            print("="*100)
            print("state analysis result: ", state["analysis_result"])
            print("="*100)
            print("\n\n\n\n\n\n\n\n\n")
            # Check if we have sufficient information using analysis_result
            print(f"Analysis result: {state.get('analysis_result', '')}")
            if state.get("analysis_result", "").startswith("SUFFICIENT: Yes"):
                print("\n\n\n\n\n\n\n\n\n")
                print("="*100)
                print("Sufficient information found. Exiting search.")
                print("="*100)
                print("\n\n\n\n\n\n\n\n\n")
                return END
            print(f"Search index: {state.get('search_index', 0)}")
            if state.get("search_index", 0) >= 3:  # Limit to 3 attempts
                print("\n\n\n\n\n\n\n\n\n")
                print("="*100)
                print("Maximum search attempts reached. Exiting search.")
                print("="*100)
                print("\n\n\n\n\n\n\n\n\n")
                return END
            print("\n\n\n\n\n\n\n\n\n")
            print("="*100)
            print("No sufficient information found. Continuing search.")
            print("="*100)
            print("\n\n\n\n\n\n\n\n\n")
            return "Search"  # Only return to Search if neither condition is met
            
        builder.add_conditional_edges(
            "Analysis",
            should_continue,
            {
                END: END,
                "Search": "Search"
            }
        )

        results = builder.compile()
        search_results = results.invoke(initial_state)
        
        # Convert SearchState back to EmailState
        return {
            "workers_called": state["workers_called"] + search_results["workers_called"],
            "messages": state["messages"] + search_results["messages"],
            "search_index": state["search_index"] + 1,
            "search_summary": search_results["search_summary"]
        }

def test_search_context(state: SearchState) -> SearchState:
    # Create a mock agent response
    print("="*100)
    print("Testing search context...")
    print("="*100)
    mock_agent_response = {
        "messages": [
            HumanMessage(content="Search query about Jake Tauscher..."),
            AIMessage(
                content="",
                additional_kwargs={
                    "tool_calls": [{
                        "id": "test_call_id",
                        "function": {
                            "name": "tavily_search",
                            "arguments": '{"query": "Jake Tauscher G2 Venture Partners"}'
                        },
                        "type": "function"
                    }]
                }
            ),
            ToolMessage(
                content="""
                SEARCH RESULTS:
                - Jake Tauscher is a Partner at G2 Venture Partners
                - Focuses on sustainable manufacturing investments
                - Led several major investment rounds
                - Specializes in industrial decarbonization
                
                ADDITIONAL CONTEXT:
                - Board member of multiple climate tech companies
                - Active in clean energy sector
                """,
                tool_call_id="test_call_id"
            )
        ]
    }
    
    # Extract search results from mock response
    search_results = ""
    for message in mock_agent_response["messages"]:
        if isinstance(message, ToolMessage):
            search_results = message.content
            break
    
    # Return updated state
    return {
        "workers_called": state["workers_called"] + ["search_agent"],
        "messages": state["messages"] + [HumanMessage(content=search_results)],
        "contact": state["contact"],
        "sender": state["sender"],
        "draft": state["draft"],
        "search_index": state["search_index"] + 1,
        "AgentCommands": None
    }

    """Process the search graph and update state."""
    
    # Create and run search graph
    graph = create_search_graph(state)
    result = graph.invoke(state)

    # Return updated state
    return {
        "workers_called": state["workers_called"] + ["process_graph"],
        "messages": state["messages"],
        "contact": state["contact"], 
        "sender": state["sender"],
        "draft": state["draft"],
        "draft_index": state["draft_index"],
        "search_index": result["search_index"],
        "search_summary": result["search_summary"],
        "AgentCommands": result["AgentCommands"]
    }