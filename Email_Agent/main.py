from email_agent import create_email_agent, draft_email
from secrets import get_secret

# Example usage
if __name__ == "__main__":
    try:
        variables = ["sender", "receiver", "context", "tone"]
        template = "Draft a {tone} email from {sender} to {receiver} regarding {context}."
        
        email_agent = create_email_agent(variables, template)
        draft = draft_email(email_agent, 
                            sender="John Doe", 
                            receiver="Jane Smith", 
                            context="project update",
                            tone="professional")
        print(draft)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
