from agents.percive_agent import percive_agent
import os
from langchain_community.agent_toolkits.load_tools import load_tools

g_agent:percive_agent = None

def give_callback(agent: percive_agent):
    global g_agent
    g_agent = agent

async def start_callback():
    pass

tools = {"searx_search":load_tools(["searx-search"],
                    searx_host=os.getenv('SEARX_URL',"http://localhost:8080"))[0]}

augmented_prompt = """"""