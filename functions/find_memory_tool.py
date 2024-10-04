from agents.percive_agent import percive_agent
from functions.qq import QQAgent
from typing import Annotated, List
from langchain.tools import tool
from model.doc import docs

g_agent:percive_agent = None
qq_agents: List[QQAgent]

def give_callback(agent: percive_agent, **kwargs):
    global g_agent, qq_agents
    g_agent = agent
    qq_agents = kwargs.get('functions.qq',[])
    for i in qq_agents:
        i.agent.add_tools(tool_factory(i.agent.state.docs_m))
        i.agent.augmented_prompts['find_memory_tool'] = augmented_prompt

async def start_callback():
    pass

def tool_factory(docs_m: docs):
    @tool
    def find_doc(uuid: Annotated[str,'The UUID of the document you want to find']):
        """Read the document detail by providing the UUID for to gain a deeper understanding"""
        doc = docs_m.find_doc(uuid=uuid,meta_on=False)
        if doc == None:
            return 'Document not found.'
        return str(doc)
    @tool
    def list_doc(all:Annotated[bool,'Turn on to find all document, Turn off to find more centralized document.']):
        """List all documents"""
        docs = docs_m.list_docs(meta_on = not all)
        return docs
    return [find_doc, list_doc]

@tool
def find_doc(uuid: Annotated[str,'The UUID of the document you want to find']):
    """Find and load the document by UUID"""
    doc = g_agent.state.docs_m.find_doc(uuid=uuid)
    if doc == None:
        return 'Document not found.'
    return str(doc)

tools = [find_doc]
loop_funcs = [start_callback]

augmented_prompt = """If the document surround by <DOC> is helpful for your current task, you can use find_doc to load the doc."""