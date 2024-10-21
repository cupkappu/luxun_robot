from langchain_core.prompts import ChatPromptTemplate
from textwrap import dedent

map_prompt=ChatPromptTemplate.from_messages(
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

reduce_prompt=ChatPromptTemplate.from_messages(
[
    ("system", """You are a helpful assistant."""),
    ('user',dedent(""" 
    <set_of_summaries>
    {context}
    </set_of_summaries>
    <INSTRUCTION>
    Take these set of summaries and distill it into a final, consolidated summary
    of the main themes.
    </INSTRUCTION>
    """)),
    ]
)