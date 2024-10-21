from langchain_core.prompts import ChatPromptTemplate
from textwrap import dedent

map_prompt=ChatPromptTemplate.from_messages(
[
    ("system", """You are an objective, calm and rational researcher."""),
    ('user',dedent(""" 
    <MEMORY>
    {context}
    </MEMORY>
    <INSTRUCTION>
    Briefly describe the topics in <MEMORY> in bulleted form.
    </INSTRUCTION>
    """)),
    ]
)

reduce_prompt=ChatPromptTemplate.from_messages(
[
    ("system", """You are an objective, calm and rational researcher."""),
    ('user',dedent(""" 
    <set_of_summaries>
    {context}
    </set_of_summaries>
    <INSTRUCTION>
    Summarize the above bullet points, extract the key points using bullet points, and give a rational and objective overall summary.
    </INSTRUCTION>
    """)),
    ]
)