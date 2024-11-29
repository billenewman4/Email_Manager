from email_agent import EmailAgent
from contacts import Contact
from sender import Sender
from secrets_ret import get_secret
from web_agent import tavily_context_search
from email_graph import run_email_workflow
from langchain_openai import ChatOpenAI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",  # For local development
        "https://email-manager-lilac.vercel.app"  # For production
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/generate-email")
async def generate_email(request_data: dict):
    print("\n=== New Email Generation Request ===")
    print(f"Contact Name: {request_data['contact_info']['name']}")
    print(f"Company: {request_data['contact_info']['company']}")

    try:
        # Initialize LLM
        openai_api_key = get_secret("OpenAPI_KEY")
        llm = ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai_api_key)

        # Create sender object from user_info
        user_info = request_data['user_info']
        sender = Sender(
            name=user_info['name'],
            resume=user_info['resume_content'],
            career_interest=user_info['career_interest'],
            key_accomplishments=user_info['key_accomplishments'],
            llm=llm
        )

        # Create contact object from contact_info
        contact_info = request_data['contact_info']
        contact = Contact({
            'Full Name': contact_info['name'],
            'Company Name': contact_info['company']
        })

        # Create EmailAgent
        email_agent = EmailAgent(contact, sender)

        # Search web for context
        print("-" * 50)
        print(f"Searching web for context for {contact.full_name} and {contact.company_name}")
        web_context = {
            'company_info': tavily_context_search(contact.company_name),
            'person_info': tavily_context_search(contact.full_name)
        }
        
        # Combine web context with user-provided context
        raw_context = (
            web_context['company_info'] + "\n" + 
            web_context['person_info'] + "\n" +
            (contact_info.get('context', '') or '')
        )
        relevant_content = email_agent.extract_relevant_content(raw_context)

        # Run email workflow
        final_state = run_email_workflow(
            email_agent=email_agent,
            sender_info=sender.get_relevant_content(),
            context=relevant_content
        )

        return {
            "email_draft": final_state["draft"]
        }

    except Exception as e:
        print(f"Error generating email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)