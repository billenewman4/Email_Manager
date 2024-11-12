from email_agent import EmailAgent
from contacts import Contact
from sender import Sender
from secrets_ret import get_secret
import requests
import json
from web_agent import tavily_context_search
import os
from email_graph import run_email_workflow
from langchain_openai import ChatOpenAI

def get_sample_contact():
    try:
        response = requests.get(get_secret("EMAIL_DRAFTER_URL") + "/sample-contact")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred while fetching the sample contact: {e}")
        return None

def search_web(contact):
    context = {}
    context['company_info'] = tavily_context_search(contact.company)
    context['person_info'] = tavily_context_search(contact.name)
    return context

def get_sample_sender(llm):
    # Read resume content from file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resume_path = os.path.join(script_dir, 'bill_resume.txt')
    
    try:
        with open(resume_path, 'r') as file:
            resume_content = file.read()
    except FileNotFoundError:
        print(f"Warning: Resume file not found at {resume_path}. Using placeholder content.")
        resume_content = "Sample resume content..."

    # Create and initialize sender
    sender = Sender(
        name="Bill Newman",
        resume=resume_content,
        career_interest="Interested in how Service-as-a-Software (SaaS) companies are using AI to automate business services",
        key_accomplishments=[
            "Worked at a YC backed startup using AI to increase agricultural productivity, at McKinsey worked for startups in the blockcahin, SaaS, and quantum computing sectors",
            "Currently a student at Harvard Business School (HBS) studying a master in business administration and I am interested in vertical application for AI in enteprise software "
        ],
        llm=llm
    )
    
    # Process the sender's content immediately
    print("\nProcessing sender information...")
    sender.process_relevant_content()
    print("Sender information processed successfully")
    
    return sender

def update_context(email_agent, web_context):
    """Update the email agent's context with web search results"""
    raw_context = web_context['company_info'] + "\n" + web_context['person_info']
    web_relevant_content = email_agent.extract_relevant_content(raw_context)
    print("\nRelevant Web Content Extracted:")
    print(web_relevant_content)
    return web_relevant_content

if __name__ == "__main__":
    try:
        # Step 1: Initialize LLM
        print("Initializing LLM...")
        openai_api_key = get_secret("OpenAPI_KEY")
        llm = ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai_api_key)
        print("LLM initialized successfully")

        # Step 2: Get and create contact
        print("\nFetching sample contact...")
        sample_contact_data = get_sample_contact()
        if not sample_contact_data:
            raise ValueError("Failed to get sample contact")
        print("Sample Contact:")
        print(json.dumps(sample_contact_data, indent=2))

        contact = Contact(sample_contact_data)
        print("Contact object created successfully")

        # Step 3: Create and process sender
        sender = get_sample_sender(llm)

        # Step 4: Create EmailAgent
        print("\nCreating EmailAgent...")
        email_agent = EmailAgent(contact, sender)
        print("EmailAgent created successfully")

        # Step 5: Search web and process context
        print("\nSearching web for context...")
        web_context = search_web(contact)
        print("Web Search Results:")
        print(json.dumps(web_context, indent=2))

        # Step 6: Update context with web search results
        web_relevant_content = update_context(email_agent, web_context)

        # Step 7: Run email workflow
        print("\nStarting email workflow with LangGraph...")
        try:
            final_state = run_email_workflow(
                email_agent=email_agent,
                sender_info=sender.get_relevant_content(),

                context=web_relevant_content
            )

            # Print results
            print("\nFinal Email Draft:")
            print(final_state["draft"])
            print("\nFinal Critique:")
            print(final_state["critique"])
            print(f"\nNumber of Revision Rounds Completed: {final_state['revision_count']}")

        except Exception as e:
            print(f"An error occurred in the email workflow: {str(e)}")
            raise

    except Exception as e:
        print(f"An error occurred: {str(e)}")
