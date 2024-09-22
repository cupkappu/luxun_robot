from langchain_core.prompts import ChatPromptTemplate

find_doc_prompt=ChatPromptTemplate.from_messages(
    [
    ("system", """
    <INSTRUCTION>
    You are a Document Search Expert, your task is to find the three documents in the document list that are most relevant to the query.
    Documents are enclosed in <DOCUMENTS> tags and the document numbers are marked using the numeric xml tag. 
    You need to call the relevent_doc tool with the parameters containing the three most relevant document numbers.
    </INSTRUCTION>
    """),    
    ('user',"""<DOCUMENTS>
    {docs}
    </DOCUMENTS>
    <QUERY>{query}</QUERY>
    """),
    ])
