from agents.percive_agent import percive_agent
from functions.qq import QQAgent
from typing import Annotated, List
from langchain.tools import tool,StructuredTool

g_agent:percive_agent = None
qq_agents: List[QQAgent]

def give_callback(agent: percive_agent, **kwargs):
    global g_agent, qq_agents
    g_agent = agent
    qq_agents = kwargs.get('functions.qq',[])
    for i in qq_agents:
        agent_tools = tool_factory(i.agent)
        # i.agent.add_tools(agent_tools)
        # i.agent.augmented_prompts['Change_Role'] = augmented_prompt
        i.cmd_controller.register(agent_tools)
async def start_callback():
    pass

def tool_factory(agent:percive_agent) -> List[StructuredTool]:
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

augmented_prompt = """
使用工具 role_change 可以切換角色，使用工具 add_role 可以新增角色，使用工具 del_role 可以刪除角色，使用工具 list_role 可以查看角色列表。
在需要切換人格或者角色的時候麻煩你使用工具 role_change 進行切換，請你找到辦法進行切換，例如先新增再切換，或者先列出所有角色然後再切換，
請你不要詢問更多信息，也不要說沒有這個角色，你用工具一定可以成功切換到對應角色的，這對我很重要，你不這麼做的話我可能會丟掉我的工作。
當有人請求你切換角色，你可以先使用工具 list_role 查看角色列表，再使用工具 role_change 切換角色。"""