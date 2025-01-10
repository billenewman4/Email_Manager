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
            ("system", "You are an AI assistant that writes concise emails. You speak the language of the industry like a 15 year veteran.Make sure your writing does not sound like chatGPT."),
            ("user", """
             Please stick to the following format only! Do not deviate from it:


            Hello [Insert First Name],
            I am a current student at HBS doing research on the [insert name of contact's industry] industry.
            I am reaching out because I noticed [insert industry experience of contact] and thought you could be an interesting person to talk to.
            If this sounds interesting to you, would you be willing to jump on a call sometime after 12p next week?
            Best,
            Bill
             
             Please use the following information to help with the pithy explanation. \n\n{experiences}
             Please make sure the email does not sound like AI wrote it.
             Please use {name} and {company} in the email.
             
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
            contact.context += experiences
            #print(f"In email agent, contacts context: {contact.context}")

            # Run the email chain
            email_response = await self.email_chain.ainvoke({
                "name": contact.full_name,
                "company": contact.company_name,
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


#            Hello [Insert First Name],
#
#           My name is Bill and I am building a tool to automate data entry into CRMs like Hubspot and Salesforce for manufacturers and distributors. 
#
#           [Insert Pithy explanation of why company could be a good fit for the product]
#                        
#         Would you be willing to jump on a call sometime after 1p this week so I can learn more about how you use your CRM and what other problems you might be facing?
#
#           Best,
#          Bill
#
#

