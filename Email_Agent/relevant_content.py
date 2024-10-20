from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import StrOutputParser
from secrets import get_secret

def create_relevant_content_extractor():
   # Retrieve the OpenAI API key from the secret manager
    api_key = get_secret('OpenAPI_KEY')
    if not api_key:
        raise ValueError("Failed to retrieve OpenAI API key from Secret Manager")
    
    # Initialize the ChatOpenAI model with the API key
    llm = OpenAI(api_key=api_key)

    # Create a prompt template
    prompt_template = PromptTemplate(
        input_variables=["raw_context", "person_name", "company_name"],
        template="""
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
    )

    # Create and return the chain
    return prompt_template | llm | StrOutputParser()

# Example usage:
# extractor = create_relevant_content_extractor()
# result = extractor.invoke({
#     "raw_context": "...",
#     "person_name": "John Doe",
#     "company_name": "Tech Innovations Inc."
# })
# print(result)
