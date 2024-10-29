from flask import Flask, request, jsonify
from email_agent import EmailAgent
from contacts import Contact
from sender import Sender
from secrets import get_secret
from web_agent import tavily_context_search
from email_graph import run_email_workflow
from langchain_openai import ChatOpenAI

app = Flask(__name__)

def initialize_llm():
    openai_api_key = get_secret("OpenAPI_KEY")
    return ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai_api_key)

def search_web(contact):
    context = {}
    context['company_info'] = tavily_context_search(contact.company)
    context['person_info'] = tavily_context_search(contact.name)
    return context

def update_context(email_agent, web_context):
    raw_context = web_context['company_info'] + "\n" + web_context['person_info']
    return email_agent.extract_relevant_content(raw_context)

@app.route('/generate-email', methods=['POST'])
def generate_email():
    try:
        data = request.json
        
        # Initialize LLM
        llm = initialize_llm()
        
        # Create Contact object
        contact_data = data.get('contact')
        if not contact_data:
            return jsonify({"error": "Contact data is required"}), 400
        contact = Contact(contact_data)
        
        # Create Sender object
        sender_data = data.get('sender')
        if not sender_data:
            return jsonify({"error": "Sender data is required"}), 400
            
        sender = Sender(
            name=sender_data.get('name'),
            resume=sender_data.get('resume'),
            career_interest=sender_data.get('career_interest'),
            key_accomplishments=sender_data.get('key_accomplishments', []),
            llm=llm
        )
        
        # Process sender information
        sender.process_relevant_content()
        
        # Create EmailAgent
        email_agent = EmailAgent(contact, sender)
        
        # Search web and process context
        web_context = search_web(contact)
        web_relevant_content = update_context(email_agent, web_context)
        
        # Run email workflow
        final_state = run_email_workflow(
            email_agent=email_agent,
            sender_info=sender.get_relevant_content(),
            context=web_relevant_content
        )
        
        return jsonify({
            "draft": final_state["draft"],
            "critique": final_state["critique"],
            "revision_count": final_state["revision_count"],
            "web_context": web_relevant_content
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
