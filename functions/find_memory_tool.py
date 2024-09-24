from agents.percive_agent import percive_agent
from typing import Annotated
from langchain.tools import tool

g_agent:percive_agent = None

def give_callback(agent: percive_agent):
    global g_agent
    g_agent = agent

async def start_callback():
    pass

@tool
def find_doc(uuid: Annotated[str,'The UUID of the document you want to find']):
    """Find and load the document by UUID"""
    doc = g_agent.state.docs_m.find_doc(uuid=uuid)
    if doc == None:
        return 'Document not found.'
    return str(doc)

tools = {'find_doc': find_doc}