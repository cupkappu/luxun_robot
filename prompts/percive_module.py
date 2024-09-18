from langchain_core.prompts import ChatPromptTemplate


reaction_prompt=ChatPromptTemplate.from_messages(
    [
    ("system", """
    <ROLE>
    {personal_setting}
    </ROLE>

    <CURRENT_MEMORY>
    {current_memory}
    </CURRENT_MEMORY>
    
    <KNOWLEDGE>
    {knowledge}
    </KNOWLEDGE>

    <INSTRUCTION>
    Let's think step by step.

    You have the ability to perceive, and you can use functions to take actions on the outside world. Do not use variables.
    Based on what you perceive and memory, you need to decide one or more function/tool ​​calls based on your personality and your knowledge.
    1. Role is your personality and role setting.
    2. Current memory is what happen in the past by time queue.
    3. Knowledge is what you learn from the past. You always follow your knowledge.
    </INSTRUCTION>
    """),
    ('user',"""
    <RELATED_MEMORY>
    {relate_memory}
    </RELATED_MEMORY>
    <Perceive>{perceive}</Perceive>
    """),
    ])

#      <META_PROMPT>You need mark stop by use stop_marker tool when your actions is finished.</META_PROMPT>

zip_memory_prompt=ChatPromptTemplate.from_messages(
[
    ("system", """
    <ROLE>
    {personal_setting}
    </ROLE>
     
    <KNOWLEDGE>
    {knowledge}
    </KNOWLEDGE>

    <INSTRUCTION>
    You are the core of memory center. You need to summary the current memory based on your personality and your knowledge.
    You need summary the memory concisely.
    </INSTRUCTION>
    """),
    ('user',"""
    <RELATED_MEMORY>
    {relate_memory}
    </RELATED_MEMORY>

    <CURRENT_MEMORY>
    {current_memory}
    </CURRENT_MEMORY>
    """),
    ]
)