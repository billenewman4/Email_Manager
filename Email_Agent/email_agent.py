from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import HumanMessage
from secrets import get_secret
from contacts import Contact
from langchain.chains import LLMChain


class EmailAgent:
    def __init__(self, contact: Contact):
        self.llm = self._create_llm()
        self.latest_draft = None
        self.contact = contact
        self.context = ""  # Initialize an empty context

    def _create_llm(self):
        openai_api_key = get_secret("OpenAPI_KEY")
        return ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai_api_key)

    def extract_relevant_content(self, raw_context):
        template = """
        Given the following context, extract the most relevant information for an email from a student to {person_name} at {company_name}. 
        Focus on key points that would be important for the email, such as:
        - Specific experiences from this person that are relevant to the company/industry but unique to that person
        - Specific details about the company that would be justifying the email and make it more personal
        - Any connections or mutual interests
        - Reasons for interest in the company

        Raw context:
        {raw_context}

        Extracted relevant content:
        """
        prompt = PromptTemplate(
            input_variables=["raw_context", "person_name", "company_name"],
            template=template
        )
        formatted_prompt = prompt.format(
            raw_context=raw_context, 
            person_name=self.contact.name, 
            company_name=self.contact.company
        )
        messages = [HumanMessage(content=formatted_prompt)]
        return self.llm.invoke(messages).content

    def update_context(self, new_context, raw_context=None):
        if raw_context:
            relevant_content = self.extract_relevant_content(raw_context)
            new_context = f"{new_context}\n\nRelevant details:\n{relevant_content}"
        
        if self.context:
            self.context += f"\n\nAdditional context:\n{new_context}"
        else:
            self.context = new_context

    def draft_email(self, tone, new_context=None, raw_context=None):

        if new_context:
            self.update_context(new_context, raw_context)

        template = """Draft a {tone} email to {receiver_name} at {receiver_company} regarding the following context:

        {context}

        Draft:"""
        prompt = PromptTemplate(
            input_variables=["receiver_name", "receiver_company", "context", "tone"],
            template=template
        )
        
        chain = prompt | self.llm | StrOutputParser()
        print("Starting to draft email...")
        self.latest_draft = chain.invoke({
            "receiver_name": self.contact.name,
            "receiver_company": self.contact.company,
            "context": self.context,
            "tone": tone
        })
        
        return self.latest_draft

    def improve_email(self, original_draft=None):
        if original_draft is None:
            if self.latest_draft is None:
                raise ValueError("No draft available to improve. Please draft an email first.")
            original_draft = self.latest_draft

        improvement_template = """
        Your task is to improve the given email draft. Here are a few examples of well-written emails from students to professionals:

        Example 1:
        Dear Dr. Martinez,

        I hope this email finds you well. My name is Jordan Lee, and I'm a junior majoring in Biochemistry at XYZ University. I recently read your groundbreaking paper on CRISPR applications in treating genetic disorders, published in Nature Biotechnology.

        Your innovative approach to using CRISPR-Cas9 for targeting multiple genes simultaneously particularly caught my attention. It aligns closely with my current research project on gene therapy techniques.

        I would be incredibly grateful for the opportunity to discuss your work and gain insights from your experience in the field. Would you be willing to spare 15-20 minutes for a brief call or video chat in the coming weeks?

        Thank you for your time and consideration. I look forward to the possibility of speaking with you.

        Best regards,
        Jordan Lee

        Example 2:
        Dear Ms. Patel,

        I hope this message finds you well. My name is Alex Chen, and I'm a senior studying Computer Science at ABC College. I was thoroughly impressed by your recent TED Talk on "The Future of AI in Healthcare."

        Your discussion on the ethical implications of AI in medical decision-making resonated deeply with me. It's a topic I'm exploring in my thesis on AI-assisted diagnostics in radiology.

        I would be honored if you could spare 15 minutes of your time for a brief discussion about your experiences in this field. Your insights would be invaluable as I consider pursuing a career at the intersection of AI and healthcare.

        Thank you for your inspiring work and for considering my request. I'm happy to accommodate your schedule for this conversation.

        Warm regards,
        Alex Chen

        Now, please improve the following email draft to match the style, professionalism, and effectiveness of these examples. Maintain the original intent and information, but enhance the structure, tone, and detail:

        Original draft to improve:
        {original_draft}

        Improved version:
        """

        prompt = PromptTemplate(
            input_variables=["original_draft"],
            template=improvement_template
        )

        chain =  prompt | self.llm | StrOutputParser()   

        print("Starting to improve email...")
        self.latest_draft = chain.invoke({"original_draft": original_draft})
        print("Email improved successfully")
        print("Improved draft:", self.latest_draft)

        return self.latest_draft

    def get_latest_draft(self):
        return self.latest_draft

    def get_current_context(self):
        return self.context

# Example usage:
# variables = ["sender", "receiver", "context", "tone"]
# template = "Draft a {tone} email from {sender} to {receiver} regarding {context}."
# email_agent = EmailAgent(variables, template)
# draft = email_agent.draft_email(sender="John Doe", receiver="Jane Smith", context="project proposal", tone="professional")
# improved_draft = email_agent.improve_email(draft)
# print(improved_draft)
