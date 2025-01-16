from Email_Agent.Object_Classes.contacts import Contact
from Email_Agent.Object_Classes.sender import Sender
from Email_Agent.Tools.secrets_ret import get_secret
from Email_Agent.Graph.draft_graph import create_email_graph
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

@app.post("/generate-email/student")
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
            'Company Name': contact_info['company'],
            'Job Title': contact_info.get('role', 'N/A'),
            'Company Description': contact_info.get('company_description', 'N/A'),
            'Location': contact_info.get('location', 'N/A'),
            'Department': contact_info.get('department', 'N/A'),
            'LinkedIn': contact_info.get('linkedin', 'N/A')
        })

        # Initialize the graph
        graph = create_email_graph("student")
        
        # Create initial state
        initial_state = {
            "input": f"Draft an email to connect to {contact.full_name} at {contact.company_name} about {user_info['career_interest']} with the intent of getting a phone call",
            "contact": contact,
            "sender": sender,
            "draft_index": 0,
            "search_index": 0,
            "AgentCommands": None
        }
        
        # Run the graph
        final_state = graph.invoke(initial_state)

        return {
            "email_draft": final_state["draft"]
        }

    except Exception as e:
        print(f"Error generating email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/test")
async def test():
    return {"message": "Hello, World!"}

@app.post("/test-email")
async def test_email():
    try:
        # Initialize LLM
        openai_api_key = get_secret("OpenAPI_KEY")
        llm = ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai_api_key)

        # Create test contact with rich information
        contact = Contact({
            "Full Name": "Ben Kortlang",
            "Job Title": "Partner",
            "Company Name": "G2 Venture Partners",
            "Company Description": "G2 Venture Partners is a venture capital firm focused on emerging technologies in traditional industries",
            "Location": "San Francisco, CA",
            "Department": "Investment Team",
            "LinkedIn": "linkedin.com/in/benkortlang"
        })

        # Create test sender with detailed background
        sender = Sender(
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
            llm=llm
        )

        # Initialize the graph
        graph = create_email_graph("student")
        
        # Create initial state
        initial_state = {
            "input": f"Draft an email to connect to {contact.full_name} at {contact.company_name} about AI/ML Venture Capital Investments with the intent of getting a phone call",
            "workers_called": [],
            "messages": [],
            "contact": contact,
            "sender": sender,
            "draft": "",
            "draft_index": 0,
            "search_index": 0,
            "search_results": "",
            "summarized_search_results": "",
            "AgentCommands": None
        }
        
        # Run the graph
        final_state = graph.invoke(initial_state)

        return {
            "email_draft": final_state["draft"],
            "search_summary": final_state.get("summarized_search_results", ""),
            "iterations": {
                "draft": final_state["draft_index"],
                "search": final_state["search_index"]
            },
            "workflow": final_state.get("workers_called", [])
        }

    except Exception as e:
        print(f"Error generating test email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Email Generation API is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)