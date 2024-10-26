from email_agent import EmailAgent
from contacts import Contact
from sender import Sender
from secrets import get_secret
import requests
import json
from web_agent import tavily_context_search
import os
from email_graph import run_email_workflow  # Add this import

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

def get_sample_sender():
    # Read resume content from file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resume_path = os.path.join(script_dir, 'bill_resume.txt')
    
    try:
        with open(resume_path, 'r') as file:
            resume_content = file.read()
    except FileNotFoundError:
        print(f"Warning: Resume file not found at {resume_path}. Using placeholder content.")
        resume_content = "Sample resume content..."

    return Sender(
        resume=resume_content,
        career_interest="Interested in how Service-as-a-Software (SaaS) companies are using AI to automate business services",
        key_accomplishments=[
            "Worked at a YC backed startup using AI to increase agricultural productivity, at McKinsey worked for startups in the blockcahin, SaaS, and quantum computing sectors",
            "At HBS, founding a startup that is buidling AI agents to automate SME manufacturing tasks"
        ]
    )

if __name__ == "__main__":
    try:
        # Step 1: Get sample contact
        sample_contact_data = get_sample_contact()
        if not sample_contact_data:
            raise ValueError("Failed to get sample contact")
        print("Sample Contact:")
        print(json.dumps(sample_contact_data, indent=2))

        # Create Contact object
        contact = Contact(sample_contact_data)
        print("\nContact object created successfully")

        # Create EmailAgent
        email_agent = EmailAgent(contact)
        print("\nEmailAgent created successfully")

        # Step 2: Search the web
        web_context = search_web(contact)
        print("\nWeb Search Results:")
        print(json.dumps(web_context, indent=2))

        # Step 3: Extract relevant content from web search and update context
        raw_context = web_context['company_info'] + "\n" + web_context['person_info']
        web_relevant_content = email_agent.extract_relevant_content(raw_context)
        print("\nRelevant Web Content Extracted:")
        print(web_relevant_content)

        email_agent.update_context("Web search results", web_relevant_content)
        print("\nContext updated with web search results")

        # Step 4: Get sender information and extract relevant content
        sender = get_sample_sender()
        sender_relevant_content = email_agent.extract_all_relevant_content(
            resume=sender.resume,
            career_interests=sender.career_interest,
            key_accomplishments="\n".join(sender.key_accomplishments)
        )
        print("\nRelevant Sender Content Extracted:")
        print(sender_relevant_content)

        email_agent.update_context("Sender information", sender_relevant_content)
        print("\nContext updated with sender information")

        # Step 5: Use the graph-based workflow for email drafting and improvement
        print("\nStarting email workflow with LangGraph...")
        try:
            final_state = run_email_workflow(
                email_agent=email_agent,
                sender_info=sender_relevant_content,
                context=f"reaching out as a student to discuss {contact.name}'s work at {contact.company}"
            )

            # Print the results of each revision
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
