from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from secrets import get_secret


def create_email_agent(variables, template):
    openai_api_key = get_secret("OpenAPI_KEY")
    llm = ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai_api_key)
    prompt = PromptTemplate(input_variables=variables, template=template)
    return LLMChain(llm=llm, prompt=prompt)


def draft_email(email_agent, **kwargs):
    return email_agent.run(**kwargs)


def improve_email_with_examples(original_draft):
    openai_api_key = get_secret("OpenAPI_KEY")
    llm = ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai_api_key)

    improvement_template = PromptTemplate(
        input_variables=["original_draft"],
        template="""
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
    )
    
    improvement_chain = LLMChain(llm=llm, prompt=improvement_template)
    improved_draft = improvement_chain.run(original_draft=original_draft)
    
    return improved_draft

# Example usage:
# template_vars = ["sender", "receiver", "context", "tone"]
# template = "Draft a {tone} email from {sender} to {receiver} regarding {context}."
# email_agent = create_email_agent(template_vars, template)
# draft = draft_email(email_agent, sender="John Doe", receiver="Jane Smith", context="project proposal", tone="professional")
# print(draft)
