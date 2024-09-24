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
def stop_marker(stop_mark: Annotated[bool, 'Mark as true to stop.']
                ) -> str:
    """Set the stop mark as true when you don't have more to do."""
    g_agent.stop_mark = stop_mark
    if stop_mark == True:
        return "<STOP_MARK_IS_TRUE />"
    return "<STOP_MARK_IS_FALSE />"

tools = {}

augmented_prompt = """"""