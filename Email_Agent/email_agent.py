from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from secrets import get_secret


def create_email_agent(template_variables, template_string):
    """
    Creates an email agent using OpenAI's language model.

    :param template_variables: List of variable names to be used in the template.
                               Example: ["sender", "receiver", "context", "tone"]
    :param template_string: A string template for the email prompt.
                            Example: "Draft a {tone} email from {sender} to {receiver} regarding {context}."
    :return: A RunnableSequence object that can be used to generate email drafts.
    """
    # Retrieve the OpenAI API key from the secret manager
    api_key = get_secret('OpenAPI_KEY')
    if not api_key:
        raise ValueError("Failed to retrieve OpenAI API key from Secret Manager")
    
    # Initialize the ChatOpenAI model with the API key
    llm = ChatOpenAI(api_key=api_key)

    # Create a PromptTemplate with the provided variables and template string
    email_draft_prompt = PromptTemplate(
        input_variables=template_variables,
        template=template_string
    )

    # Create the email draft chain
    email_draft = email_draft_prompt | llm | StrOutputParser()

    # Create the email analysis prompt
    email_analysis_prompt = ChatPromptTemplate.from_template("Is this a good email? {email}")

    # Create and return the final chain
    return (
        {"email": email_draft} 
        | email_analysis_prompt 
        | llm 
        | StrOutputParser()
    )

def draft_email(agent, **kwargs):
    """
    Generates an email draft using the provided email agent and input parameters.

    :param agent: A RunnableSequence object created by the create_email_agent function.
    :param kwargs: Keyword arguments that match the template_variables defined in create_email_agent.
    :return: A string containing the generated email draft and its analysis.
    """
    return agent.invoke(kwargs)

# Example usage:
# template_vars = ["sender", "receiver", "context", "tone"]
# template = "Draft a {tone} email from {sender} to {receiver} regarding {context}."
# email_agent = create_email_agent(template_vars, template)
# draft = draft_email(email_agent, sender="John Doe", receiver="Jane Smith", context="project proposal", tone="professional")
# print(draft)
