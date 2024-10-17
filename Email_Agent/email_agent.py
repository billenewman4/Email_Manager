from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from secrets import get_secret


def create_email_agent(template_variables, template_string):
    """
    Creates an email agent using OpenAI's language model.

    :param template_variables: List of variable names to be used in the template.
                               Example: ["sender", "receiver", "context"]
    :param template_string: A string template for the email prompt.
                            Example: "Write an email from {sender} to {receiver} about {context}."
    :return: An LLMChain object that can be used to generate email drafts.

    This function sets up the language model and prompt template for email generation.
    It retrieves the OpenAI API key from a secret manager and initializes the ChatOpenAI model.
    """
    # Retrieve the OpenAI API key from the secret manager
    api_key = get_secret('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("Failed to retrieve OpenAI API key from Secret Manager")
    
    # Initialize the ChatOpenAI model with the API key
    llm = ChatOpenAI(api_key=api_key)

    # Create a PromptTemplate with the provided variables and template string
    prompt = PromptTemplate(
        input_variables=template_variables,
        template=template_string
    )

    # Return an LLMChain that combines the language model and prompt template
    return LLMChain(llm=llm, prompt=prompt)

def draft_email(agent, **kwargs):
    """
    Generates an email draft using the provided email agent and input parameters.

    :param agent: An LLMChain object created by the create_email_agent function.
    :param kwargs: Keyword arguments that match the template_variables defined in create_email_agent.
                   Example: sender="John", receiver="Jane", context="meeting schedule"
    :return: A string containing the generated email draft.

    This function takes the email agent and the necessary input parameters to generate
    an email draft based on the defined template.
    """
    return agent.run(**kwargs)

# Example usage:
# template_vars = ["sender", "receiver", "context"]
# template = "Write a professional email from {sender} to {receiver} regarding {context}."
# email_agent = create_email_agent(template_vars, template)
# draft = draft_email(email_agent, sender="John Doe", receiver="Jane Smith", context="project proposal")
# print(draft)
