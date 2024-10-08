from langchain_core.prompts import ChatPromptTemplate
from textwrap import dedent

prompt=ChatPromptTemplate.from_messages(
[
    ("system", """You are a helpful assistant."""),
    ('user',dedent(""" 
    <MEMORY>
    {context}
    </MEMORY>
    <INSTRUCTION>
    You need give the content surrounded by <MEMORY> a concise summary.
    </INSTRUCTION>
    """)),
    ]
)