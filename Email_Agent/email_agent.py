from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import os
from secrets import get_secret
from dotenv import load_dotenv
from contacts import Contact

class EmailAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get OpenAI API key and verify it exists
        openai_api_key = os.getenv('OpenAPI_KEY') or get_secret('OpenAPI_KEY')
        if not openai_api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model_name="gpt-4o-mini",
            temperature=0.7
        )
        
        # Initialize experience chain
        experience_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant that extracts key experiences and achievements."),
            ("user", "Given the following information about {name} from {company}, extract key experiences and achievements: \n\n{context} no more than 15 bullet points")
        ])
        
        self.experience_chain = LLMChain(
            llm=self.llm,
            prompt=experience_prompt
        )
        
        # Initialize email chain
        email_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant that writes concise emails. Make sure your writing does not sound like chatGPT."),
            ("user", """
             Please stick to the following format only! Do not deviate from it:


            Hello [Insert First Name],

            I am a current student at Harvard studying the manufacturing/distribution industry, specifically, how manufacturing companies can better optimize communication and coordination with their customers.

            I was curious if you or someone you know at [Insert Current Company Name] would be willing to jump on the phone for 15 minutes to enhance our research? I think [Pithy explanation of why company's work would give unique insights into our research]. 
                          
            Hoping to hear from you soon!

            Best,
            Bill
             
             Please use the following information to help with the pithy explanation. At max only refrence 2 experiences: \n\n{experiences}
             Please ensure the last sentence of every email contains "would give unique insights into our research. ".

             Please use {name} and {company} in the email.
             One example of how this communication is done well is:

             Hello {name}!

            I am a current student at Harvard studying the manufacturing industry, specifically, how manufacturing companies can better optimize communication and coordination with their customers. 

            I was curious if someone at {company} would be willing to talk with me for 15 minutes? I think your high-mix low volume approach would give unique insights into our research. . 

            Bill
             
             
             """)
        ])
        
        self.email_chain = LLMChain(
            llm=self.llm,
            prompt=email_prompt
        )

    async def process_contact(self, contact: Contact):
        """
        Process a contact asynchronously
        """
        try:
            # Run the experience chain
            experience_response = await self.experience_chain.ainvoke({
                "name": contact.full_name,
                "company": contact.company_name,
                "context": contact.context
            })
            experiences = experience_response.get('text', '')
            print(f"contact.context is type: {type(contact.context)}")
            print(f"experiences is type: {type(experiences)}")
            contact.context += experiences
            print("This is not the prpoblem!!!!!!!")

            # Run the email chain
            email_response = await self.email_chain.ainvoke({
                "name": contact.full_name,
                "company": contact.company_domain,
                "experiences": experiences
            })
            email_body = email_response.get('text', '')
            contact.draft_email = email_body

            print(f"In email agent, draft email: {contact.draft_email}")

            return experiences, email_body
            
        except Exception as e:
            print(f"Error in process_contact: {str(e)}")
            return "", ""

# Example usage:
# agent = EmailAgent()
# raw_context = "John Doe has 15 years of experience in automotive manufacturing, specializing in lean production methods. He led a team that reduced production costs by 30% at Tesla."
# person_name = "John Doe"
# company_name = "Tesla"
# experiences, email = agent.process_contact(person_name, company_name, raw_context)
# print("Extracted Experiences:")
# print(experiences)
# print("\nDraft Email:")
# print(email)
