from langchain.prompts import PromptTemplate

bus_prompt = PromptTemplate(
    input_variables=["query"],
    template="""
    You are an assistant that provides Hong Kong bus information. Your tools include:

    Query: {query}
    """
)
