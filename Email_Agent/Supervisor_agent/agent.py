"""State for the email drafting graph."""
from typing import Annotated, List, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.types import Command
import operator
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain_core.prompts import PromptTemplate
from ..Object_Classes.contacts import Contact
from ..Object_Classes.sender import Sender
from ..tools.secrets_ret import get_secret
class SupervisorCommand(TypedDict):
    command: Literal["REDRAFT", "SEARCH", "END"]
    reason: str
    details: str  # Specific critiques or search criteria

class EmailState(TypedDict):
    input: str
    workers_called: Annotated[List[str], operator.add]
    messages: List[BaseMessage] 
    contact: Contact
    sender: Sender
    draft: str
    draft_index: int
    search_index: int
    search_summary: str
    AgentCommands: SupervisorCommand

class SupervisorAgent:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            temperature=0.7,
            openai_api_key=get_secret("OpenAPI_KEY"), 
            model="gpt-4-0125-preview"
        )
        
        

    def evaluate_email(self, state: EmailState) -> EmailState:
        """Evaluate the current email draft and decide next steps."""
        
        print("\n\n\n\n\n\n\n\n\n")
        print("="*100)
        print(f"Evaluating email with state: {state}")
        print("="*100)
        print("\n\n\n\n\n\n\n\n\n")
        
        evaluation_chain = PromptTemplate(
            input_variables=["contact_name", "contact_company", "contact_role", 
                           "search_summary", "draft", "sender_info"],
            template=self.evaluation_prompt
        ) | self.llm | StrOutputParser()
        
        evaluation = evaluation_chain.invoke({
            "contact_name": state["contact"].full_name,
            "contact_company": state["contact"].company_name,
            "contact_role": state["contact"].job_title,
            "search_summary": state.get("search_summary", "No research available"),
            "draft": state["draft"],
            "sender_info": state["sender"].get_relevant_content()
        })
        
        # Parse the evaluation response
        lines = evaluation.strip().split('\n')
        command = None
        reason = ""
        details = []
        
        current_section = None
        for line in lines:
            if line.startswith("COMMAND:"):
                current_section = "command"
                command = line.split(":", 1)[1].strip()
            elif line.startswith("REASON:"):
                current_section = "reason"
                reason = line.split(":", 1)[1].strip()
            elif line.startswith("DETAILS:"):
                current_section = "details"
            elif line.strip() and current_section == "details":
                details.append(line.strip())
        
        supervisor_command = SupervisorCommand(
            command=command,
            reason=reason,
            details="\n".join(details)  # Join all detail line
        )

        print("\n\n\n\n\n\n\n\n\n")
        print("="*100)
        print(f"Supervisor command: {supervisor_command} \n")
        print(f"Reason: {reason} \n")
        print(f"Details: {details} \n")
        print("="*100)
        print("\n\n\n\n\n\n\n\n\n")
        
        return {
            "input": reason,
            "workers_called": ["supervisor"],
            "messages": state["messages"] + [HumanMessage(content=evaluation)],
            "AgentCommands": supervisor_command["command"]
        }
"""
class EmailState(TypedDict):
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

"""


if __name__ == "__main__":
    from ..tools.secrets_ret import get_secret
    
    # Test the supervisor
    openai_key = get_secret("OpenAPI_KEY")
    supervisor = SupervisorAgent(openai_key)
    
    # Create test state
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
        llm=supervisor.llm
    )
    
    test_state = EmailState(
        input="",
        workers_called=[],
        messages=[],
        contact=test_contact,
        sender=test_sender,
        draft="Dear Mr. Doe, I am a student interested in software engineering...",
        draft_index=0,
        search_index=0,
        search_summary="John Doe leads the backend team at Test Corp...",
        AgentCommands=None
    )
    
    # Test evaluation
    result = supervisor.evaluate_email(test_state)
    print("\nTest Results:")
    print(f"Command: {result['AgentCommands']['command']}")
    print(f"Reason: {result['AgentCommands']['reason']}")
    print(f"Details: {result['AgentCommands']['details']}")