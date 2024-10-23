from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from secrets import get_secret

class EmailAgent:
    def __init__(self):
        self.api_key = self._get_api_key()
        self.llm = ChatOpenAI(api_key=self.api_key)
        self.experience_extractor = self._create_experience_extractor()
        self.email_generator = self._create_email_generator()

    def _get_api_key(self):
        api_key = get_secret('OpenAPI_KEY')
        if not api_key:
            raise ValueError("Failed to retrieve OpenAI API key from Secret Manager")
        return api_key

    def _create_experience_extractor(self):
        prompt_template = PromptTemplate(
            input_variables=["raw_context", "person_name", "company_name"],
            template="""
            Given the following context about {person_name} at {company_name}, list 5-10 bullet points 
            of their experiences or achievements related to manufacturing:

            Context:
            {raw_context}

            Output the bullet points in the following format:
            - Experience 1
            - Experience 2
            - ...
            """
        )
        return prompt_template | self.llm | StrOutputParser()

    def _create_email_generator(self):
        prompt_template = PromptTemplate(
            input_variables=["experiences", "person_name", "company_name"],
            template="""
            Given the following experiences of {person_name} at {company_name}, draft an email using this outline:

            Hello {person_name},

            I am a current student at Harvard doing research into the manufacturing space. [Insert a sentence here that naturally incorporates the most relevant experience or achievement from the list, in a way that shows why you're reaching out to them specifically.] We thought you would have good insights for us.

            Would you be willing to talk with us for 15 minutes?

            Best regards,
            Bill

            Experiences:
            {experiences}

            Please draft the complete email, ensuring that the inserted sentence flows naturally within the context of the email:
            """
        )
        return prompt_template | self.llm | StrOutputParser()

    def process_contact(self, person_name, company_name, raw_context):
        experiences = self.extract_experiences(raw_context, person_name, company_name)
        email = self.generate_email(experiences, person_name, company_name)
        return experiences, email

    def extract_experiences(self, raw_context, person_name, company_name):
        return self.experience_extractor.invoke({
            "raw_context": raw_context,
            "person_name": person_name,
            "company_name": company_name
        })

    def generate_email(self, experiences, person_name, company_name):
        return self.email_generator.invoke({
            "experiences": experiences,
            "person_name": person_name,
            "company_name": company_name
        })

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
