from langchain_openai import ChatOpenAI
import os
llm = ChatOpenAI(
    base_url=os.environ['OPENAI_BASE_URL'],
    api_key=os.environ['OPENAI_API_KEY'],
    model=os.environ['OPENAI_MODEL'],
    temperature=float(os.environ['OPENAI_TEMP']))
