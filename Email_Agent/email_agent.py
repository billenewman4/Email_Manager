from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import HumanMessage
from secrets import get_secret
from contacts import Contact
from sender import Sender
from langchain.chains import LLMChain


class EmailAgent:
    def __init__(self, contact: Contact, sender: Sender):
        self.llm = self._create_llm()
        self.latest_draft = None
        self.sender = sender
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

    def draft_email(self, tone, sender_info, new_context=None, raw_context=None):
        if new_context:
            self.update_context(new_context, raw_context)

        template = """Draft a {tone} email from a student to {receiver_name} at {receiver_company} regarding the following context:

        Receiver Context:
        {receiver_context}

        Sender Information:
        {sender_info}

        Email Purpose:
        {email_purpose}

        Consider the following guidelines:
        1. Briefly introduce yourself using relevant information from the sender's background. (optional)
        2. Explain the purpose of your email, relating it to the receiver's work or company. Please note the sender will be reaching out about the current company the reciever is working at.
        3. Highlight 1-2 key points from your background that are most relevant to the receiver or their company.
        4. Express your interest in the company or the receiver's work, using specific details from the receiver context. If parallels exist in background (for example worked at the same company before), mention them but if nothing exists do not force it.
        5. Include a clear call to action or request (e.g., a brief meeting, a response to a question).
        6. Close with a polite and professional sign-off.

        A few notes:
        - The sender is a student reaching out to the receiver, but the email should not be too cringy or too excited.
        - The sender is reaching out about the current company the receiver is working at.
        - You do not have to use every single detail from the receiver context, only use what is most relevant.
        - The sender is not trying to sell themselves, they are reaching out to learn more about the receiver's work and the company.

        Draft:"""

        prompt = PromptTemplate(
            input_variables=["tone", "receiver_name", "receiver_company", "receiver_context", "sender_info", "email_purpose"],
            template=template
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        print("Sending request to LLM...")
        self.latest_draft = chain.invoke({
            "tone": tone,
            "receiver_name": self.contact.name,
            "receiver_company": self.contact.company,
            "receiver_context": self.context,
            "sender_info": sender_info,
            "email_purpose": f"reaching out as a student to discuss {self.contact.name}'s work at {self.contact.company}"
        })
        print("Received response from LLM")
        print("Draft email:", self.latest_draft)
        print("Email drafted successfully")
        
        return self.latest_draft

    def improve_email(self, original_draft=None):
        if original_draft is None:
            if self.latest_draft is None:
                raise ValueError("No draft available to improve. Please draft an email first.")
            original_draft = self.latest_draft

        improvement_template = """
        Your task is to improve the given email draft. Here are a few examples of well-written emails from students to professionals. Please modify the email to match the tone and style as well as using the structure and sender examples as inspiration:

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

        Now, please improve the following email draft to match the style, tone, and structure of the examples. 

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

    def critique_email(self, draft):
        template = """
        Evaluate the following email draft and provide specific critiques. Focus on:
        1. As a student is this an email I would feel comfortable sending to a professional. Do I come accross as overally professional or bragging?
        2. Does this email sound unique to the sender/reciever or is it generic (e.g., something almost any student could send)
        3. Is every word or detail in the email in some way relevant to the reciever? 
        4. Is the email pithy enough? These are busy professionals that don't have a ton of time to read long emails

        Please be extremely critical with your feedback for best results

        For each aspect, provide:
        - Specific feedback
        - Suggested improvements

        Email Draft:
        {draft}

        Critique:
        """
        
        prompt = PromptTemplate(
            input_variables=["draft"],
            template=template
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"draft": draft})

    def revise_with_critique(self, draft, critique):
        template = """
        Revise the following email draft based on the provided critique. 
        Maintain the core message while addressing the specific feedback points.

        Original Draft:
        {draft}

        Critique:
        {critique}

        Revised Draft:
        """
        
        prompt = PromptTemplate(
            input_variables=["draft", "critique"],
            template=template
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "draft": draft,
            "critique": critique
        })

    def update_context(self, new_context, raw_context=None):
        """Update the email agent's context with new information
        
        Args:
            new_context (str): The new context to be added
            raw_context (str, optional): Raw context that needs processing before adding
        """
        if raw_context:
            # Process raw context first
            processed_context = self.extract_relevant_content(raw_context)
            self.context = processed_context
        else:
            # If no raw context, just update with new context
            self.context = new_context
        
        print("Context updated successfully")
        return self.context

# Example usage:
# variables = ["sender", "receiver", "context", "tone"]
# template = "Draft a {tone} email from {sender} to {receiver} regarding {context}."
# email_agent = EmailAgent(variables, template)
# draft = email_agent.draft_email(sender="John Doe", receiver="Jane Smith", context="project proposal", tone="professional")
# improved_draft = email_agent.improve_email(draft)
# print(improved_draft)





