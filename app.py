from Email_Agent.Object_Classes.contacts import Contact
from Email_Agent.Object_Classes.sender import Sender
from Email_Agent.Tools.secrets_ret import get_secret
from Email_Agent.Graph.draft_graph import create_email_graph
from langchain_openai import ChatOpenAI
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from fastapi.responses import JSONResponse
from Email_Agent.Tools.email_sender import send_email

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://email-manager-lilac.vercel.app",  # Production
        "https://email-agent-1085470808659.us-west2.run.app"  # Cloud Run URL
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers for now to debugs
    expose_headers=["*"],
    max_age=3600,
)

@app.options("/generate-email/student")
async def options_email(request: Request):
    """Handle OPTIONS requests explicitly"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": request.headers.get("Origin", "*"),
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "3600",
        },
    )

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"\n=== Incoming {request.method} Request ===")
    print(f"URL: {request.url}")
    print(f"Headers: {request.headers}")
    response = await call_next(request)
    print(f"Response Status: {response.status_code}")
    return response

@app.post("/generate-email/student/batch")
async def generate_email_batch(request: Request):
    """
    Generate multiple emails from an array of contacts.
    Expected format:
    {
        "user_info": {
            "name": "Name",
            "resume_content": "...",
            "career_interest": "...",
            "key_accomplishments": [...]
        },
        "contacts": [
            {
                "contact_info": {
                    "name": "Name",
                    "company": "Company",
                    "role": "Role"
                }
            },
            ...
        ]
    }
    """
    try:
        body = await request.json()
        print(f"Request Body: {body}")
        
        if not isinstance(body.get('contacts'), list):
            return JSONResponse(
                status_code=400,
                content={"error": "Request must contain a 'contacts' array"}
            )

        if not body.get('user_info'):
            return JSONResponse(
                status_code=400,
                content={"error": "Request must contain 'user_info'"}
            )

        results = []
        for contact in body['contacts']:
            try:
                print(f"Processing contact: {contact['contact_info']}")
                print(f"User Info: {body['user_info']}")
                
                # Create the properly formatted request for generate_email
                email_request = {
                    "user_info": body['user_info'],
                    "contact_info": contact['contact_info']
                }
                
                # Pass the dictionary directly to generate_email
                result = await generate_email(email_request)
                results.append({
                    "success": True,
                    "result": result,
                    "contact": contact['contact_info']
                })
            except Exception as e:
                print(f"Error processing contact {contact['contact_info']['name']}: {str(e)}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "contact": contact['contact_info']
                })

        return {
            "batch_results": results,
            "total_processed": len(results),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"])
        }

    except Exception as e:
        print(f"Batch processing failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Batch processing failed: {str(e)}"}
        )

@app.post("/generate-email/student")
async def generate_email(request: Request):
    try:
        # Handle both Request objects and dictionaries
        if isinstance(request, dict):
            body = request
        else:
            body = await request.json()
            
        print("\n=== Email Generation Request ===")
        print(f"Request Body: {body}")
        
        print("\n=== New Email Generation Request ===")
        print(f"Contact Name: {body['contact_info']['name']}")
        print(f"Company: {body['contact_info']['company']}")

        # Initialize LLM
        openai_api_key = get_secret("OpenAPI_KEY")
        llm = ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai_api_key)

        # Create sender object from user_info
        user_info = body['user_info']
        sender = Sender(
            name=user_info['name'],
            resume=user_info['resume_content'],
            career_interest=user_info['career_interest'],
            key_accomplishments=user_info['key_accomplishments'],
            llm=llm
        )
        # Create contact object from contact_info
        contact_info = body['contact_info']
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
            "AgentCommands": None,
            "workers_called": [],
            "messages": [],
            "draft": "",
            "search_results": "",
            "summarized_search_results": ""
        }
        
        # Run the graph
        print("Graph Invoked")
        final_state = graph.invoke(initial_state)

        send_email(final_state["draft"])

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
            "search_summary": "",
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