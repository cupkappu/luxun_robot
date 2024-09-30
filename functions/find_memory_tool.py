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

async def start_callback():
    pass

def tool_factory(docs_m: docs):
    @tool
    def find_doc(uuid: Annotated[str,'The UUID of the document you want to find']):
        """Find and load the document by UUID"""
        doc = docs_m.find_doc(uuid=uuid)
        if doc == None:
            return 'Document not found.'
        return str(doc)
    return [find_doc]

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