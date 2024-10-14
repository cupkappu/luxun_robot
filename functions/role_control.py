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
    def role_change(Role_id: Annotated[str, 'The uuid of the role you want to change.'],):
        """Change your role prompt by call this tool. If you don't know any role id, you can use tool list_role to get all the role id."""
        return agent.state.setting_mng.set_default(Role_id)

    @tool
    def add_role(Role_description: Annotated[str, 'The description of the role you want to add.'],):
        """Add a new role to the role setting list. """
        newrole = agent.state.setting_mng.gen(Role_description)
        return {"state":"sussess","new_role":newrole.to_dict(base=True)}

    @tool
    def list_role():
        """List all the role in the role setting list. """
        roles = agent.state.setting_mng.list_all()
        role_list = [i.to_dict(base=True) for i in roles]
        return role_list

    @tool
    def del_role(Role_id: Annotated[str, 'The id of the role you want to delete.'],):
        """Delete a role from the role setting list. If you don't know any role id, you can use tool list_role to get all the role id."""
        setting = agent.state.setting_mng.find(Role_id)
        agent.state.setting_mng.delete(Role_id)
        return f"Role {setting.name} has been deleted."

    return [role_change, add_role, list_role, del_role]

tools = []
loop_funcs = [start_callback]

augmented_prompt = """當用戶請求你切換角色，你可以先使用工具 list_role 查看角色列表，再使用工具 role_change 切換角色。"""