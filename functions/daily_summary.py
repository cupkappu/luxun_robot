from agents.percive_agent import percive_agent
from functions.qq import QQAgent
from typing import Annotated, List
from langchain.tools import tool

g_agent:percive_agent = None
qq_agents: List[QQAgent]

def give_callback(agent: percive_agent, **kwargs):
    global g_agent, qq_agents
    g_agent = agent
    qq_agents = kwargs.get('functions.qq',[])
    for i in qq_agents:
        i.agent.add_tools(tool_factory(i.agent))
        i.agent.augmented_prompts[''] = augmented_prompt

async def start_callback():
    pass

def tool_factory(agent:percive_agent):
    @tool
    def example_tool():
        pass
    return [example_tool]

tools = []
loop_funcs = [start_callback]

augmented_prompt = """"""