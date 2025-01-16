"""State for the email drafting graph."""
from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.types import Command
import operator
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from ..Tools.secrets_ret import get_secret
from ..Object_Classes.contacts import Contact
from ..Object_Classes.sender import Sender
from .prompts import get_prompt
class EmailState(TypedDict):
    input: str
    workers_called: Annotated[List[str], operator.add]
    messages: List[BaseMessage] 
    contact: Contact
    sender: Sender
    draft: str
    draft_index: int
    search_index: int
    AgentCommands: Command

class DraftingAgent:
    def __init__(self, worker_name: str, user_type: str):
        print("Initializing DraftingAgent...")
        self.llm = ChatOpenAI(
            temperature=0.7,
            openai_api_key=get_secret("OpenAPI_KEY"), 
            model="gpt-4-0125-preview"
        )
        self.prompt = get_prompt(user_type)
        self.worker_name = worker_name
        self.latest_draft = None
        print(f"Drafting agent initialized with {self.worker_name}")

    def draft_email(self, state: EmailState) -> EmailState:
        print("\n\n\n\n\n\n\n\n\n")
        print("="*100)
        print(f"Drafting email with state: {state}")
        print("="*100)
        print("\n\n\n\n\n\n\n\n\n")
        


        prompt = PromptTemplate(
            input_variables=["tone", "receiver_name", "receiver_company", "receiver_context", "sender_info", "email_purpose"],
            template=self.prompt
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        
        print("="*100)
        print("Sending request to LLM...")
        print(f"request includes receiver context: {state.get('search_summary', 'No additional context available')}")
        print("="*100)
        print("\n\n\n\n\n\n\n\n\n")
        self.latest_draft = chain.invoke({
            "tone": "professional",
            "receiver_name": state["contact"].full_name,
            "receiver_company": state["contact"].company_name,
            "receiver_context": state.get("search_summary", "No additional context available"),
            "sender_info": state["sender"].get_relevant_content(),
            "email_purpose": f"reaching out as a student to discuss {state['contact'].full_name}'s work at {state['contact'].company_name}"
        })
        print("\n\n\n\n\n\n\n\n\n")
        print("="*100)
        print("Received response from LLM")
        print("Draft email:", self.latest_draft)
        print("Email drafted successfully")
        print("="*100)
        print("\n\n\n\n\n\n\n\n\n")
        
        return {
            "input": state["input"],
            "workers_called": [self.worker_name],
            "messages": state["messages"] + [HumanMessage(content=self.latest_draft)],
            "draft": self.latest_draft,
            "draft_index": state["draft_index"] + 1,
        }
    
if __name__ == "__main__":
    # Get API key
    openai_key = get_secret("OpenAPI_KEY")
    
    # Create test drafting agent
    test_prompt = """You are an AI assistant that drafts professional emails.
    Keep the tone professional but friendly.
    Focus on clear communication and actionable next steps."""
    
    agent = DraftingAgent(
        openai_api_key=openai_key,
        tools=[],
        worker_name="test_drafting_agent", 
        system_message=test_prompt
    )
    
    # Test state
    test_contact = Contact({
        "Full Name": "John Doe",
        "Job Title": "Senior Software Engineer",
        "Company Name": "Test Corp"
    })
    
    test_sender = Sender(
        name="Test Student",
        resume="Computer Science student",
        career_interest="Software Engineering",
        key_accomplishments=["Dean's List"],
        llm=agent.llm
    )
    
    test_state = EmailState(
        input="Draft test email",
        workers_called=[],
        messages=[],
        contact=test_contact,
        sender=test_sender,
        draft="",
        draft_index=0,
        search_index=0,
        AgentCommands=None
    )
    
    # Run test
    print("\nTesting draft_email function...")
    result = agent.draft_email(test_state)
    
    print("\nTest Results:")
    print(f"Draft content: {result['draft']}")
    print(f"Workers called: {result['workers_called']}")
    print(f"Draft index: {result['draft_index']}")