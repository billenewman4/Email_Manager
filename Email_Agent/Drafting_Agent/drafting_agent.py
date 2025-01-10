"""State for the email drafting graph."""
from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.types import Command
import operator
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from ..secrets_ret import get_secret
from ..contacts import Contact
from ..sender import Sender

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
    def __init__(self, openai_api_key: str, worker_name: str):
        print("Initializing DraftingAgent...")
        self.llm = ChatOpenAI(
            temperature=0.7,
            openai_api_key=openai_api_key, 
            model="gpt-4-0125-preview"
        )
        self.worker_name = worker_name
        self.latest_draft = None
        print(f"Drafting agent initialized with {self.worker_name}")

    def draft_email(self, state: EmailState) -> EmailState:
        print("\n\n\n\n\n\n\n\n\n")
        print("="*100)
        print(f"Drafting email with state: {state}")
        print("="*100)
        print("\n\n\n\n\n\n\n\n\n")
        
        template = """Draft a {tone} email from a student to {receiver_name} at {receiver_company} regarding the following context:

        Receiver Context:
        {receiver_context}

        Sender Information:
        {sender_info}

        Email Purpose:
        {email_purpose}

        Consider the following guidelines:
        1. Briefly introduce yourself using relevant information from the sender's background. (optional)
        2. Explain the purpose of your email, relating it to the receiver's work or company. Please note the sender will be reaching out about the current company the reciever is working at.
        3. Highlight 1-2 key points from your background that are most relevant to the receiver or their company.
        4. Express your interest in the company or the receiver's work, using specific details from the receiver context. If parallels exist in background (for example worked at the same company before), mention them but if nothing exists do not force it.
        5. Include a clear call to action or request (e.g., a brief meeting, a response to a question).
        6. Close with a polite and professional sign-off.

        A few notes:
        - The sender is a student reaching out to the receiver, but the email should not be too cringy or too excited.
        - The sender is reaching out about the current company the receiver is working at.
        - You do not have to use every single detail from the receiver context, only use what is most relevant.
        - The sender is not trying to sell themselves, they are reaching out to learn more about the receiver's work and the company.
        - This email should not sound like it was written by chatGPT!!!
        - Do NOT brag in any way about the sender's background, achievements, or anything else.
        - Do NOT use the sender's name in the email.

        Draft:"""

        prompt = PromptTemplate(
            input_variables=["tone", "receiver_name", "receiver_company", "receiver_context", "sender_info", "email_purpose"],
            template=template
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        print("Sending request to LLM...")
        self.latest_draft = chain.invoke({
            "tone": "professional",
            "receiver_name": state["contact"].full_name,
            "receiver_company": state["contact"].company_name,
            "receiver_context": state["contact"].job_title,
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
            "contact": "", # Preserve contact
            "sender": "", # Preserve sender
            "draft": self.latest_draft,
            "draft_index": state["draft_index"] + 1,
            "search_index": "", # Preserve search index
            "AgentCommands": "" # No new command to add ... always routes back to supervisor
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