from agents.percive_agent import percive_agent
from typing import Annotated
from langchain.tools import tool

g_agent:percive_agent = None

def give_callback(agent: percive_agent, **kwargs):
    global g_agent
    g_agent = agent

async def start_callback():
    pass

tools = []
loop_funcs = [start_callback]

augmented_prompt = """"""