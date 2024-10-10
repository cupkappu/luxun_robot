"""
使用mongodb存儲Role setting, 並設計tools讓agent可以訪問role setting，並且可以設定role prompt。
即爲：
- 設計數據庫結構
- 設計tools
"""

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
        i.agent.augmented_prompts['Change_Role'] = augmented_prompt

async def start_callback():
    pass

def tool_factory(agent:percive_agent):
    @tool
    def role_change(Role_id: Annotated[str, 'The id of the role you want to change.'],):
        pass
    @tool
    def add_role(Role_description: Annotated[str, 'The description of the role you want to add.'],):
        pass
    @tool
    def list_role():
        pass
    @tool
    def del_role(Role_id: Annotated[str, 'The id of the role you want to delete.'],):
        pass
    return [role_change,add_role,list_role,del_role]

tools = []
loop_funcs = [start_callback]

augmented_prompt = """你可以使用"""