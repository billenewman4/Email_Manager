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
            openai_api_key=openai_api_key, 
            model="gpt-4-0125-preview"
        )
        
        self.evaluation_prompt = """You are a supervisor evaluating an email draft. Your job is to determine if the email needs revision because the wording is bad, needs more research (e.g., like a google search to learn more about the contact), or is ready to send.

        Contact Information:
        Name: {contact_name}
        Company: {contact_company}
        Role: {contact_role}

        Research Summary:
        {search_summary}

        Current Draft:
        {draft}

        Sender Information:
        {sender_info}

        Evaluate the email based on these criteria:
        1. Does it effectively use the research about the contact?
        2. Is the tone appropriate for a student reaching out?
        3. Is it personalized and specific enough or could the same email be sent to multiple contacts? Does it mention something specific about this persons background or is it generic?
        4. Does it have a clear purpose and call to action?
        5. Does it avoid common mistakes (being too pushy, too formal, or too casual)?
        6. Is the email tailored to the receiver's company and role?
        7. Is the email tailored to the sender's background and interests?
        8. Is the email over wordy
        9. Does the email sound like it was written by chatGPT?

        Response optionsn are: 
        REDRAFT: The email needs revision because the wording is bad, needs more research, or is not personalized enough.
        SEARCH: The email needs more research because the contact information is not specific enough.
        END: The email is ready to send.

        Please be a tough critic

        Respond in the following format:
        COMMAND: [REDRAFT/SEARCH/END]
        REASON: [Brief explanation of your decision]
        DETAILS: [If REDRAFT: specific critiques and suggestions, If SEARCH: specific information to look for, If END: brief confirmation of why email is ready]
        """

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