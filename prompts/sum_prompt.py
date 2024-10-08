from langchain_core.prompts import ChatPromptTemplate
from textwrap import dedent

prompt=ChatPromptTemplate.from_messages(
[
    ("system", """You are a helpful assistant."""),
    ('user',dedent(""" 
    <CURRENT_MEMORY>
    {content}
    </CURRENT_MEMORY>
    <INSTRUCTION>
    You need give the content surrounded by <CURRENT_MEMORY> a concise summary.
    </INSTRUCTION>
    """)),
    ]
)