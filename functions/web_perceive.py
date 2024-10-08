from quart import Quart, jsonify, request, render_template
from agents.percive_agent import percive_agent
from functions.qq import find_qq_agent_by_no, QQAgent
from typing import List

g_agent:percive_agent = None
qq_agents: List[QQAgent]

def give_callback(agent: percive_agent, **kwargs):
    global g_agent, qq_agents
    g_agent = agent
    qq_agents = kwargs['functions.qq']

app: Quart = Quart(__name__,template_folder='./html_template/')

async def start_callback():
    config = {"host": "0.0.0.0", "port": 5000, "debug": False}
    await app.run_task(**config)

@app.route('/add_perceive', methods=['POST'])
async def add_perceive():
    json_data = await request.get_json()
    g_agent.perceives.append(json_data)
    return jsonify({"message": f"Perceive added: {json_data}"})

@app.route('/get_qq_prompt/<group_no>')
async def get_qq_prompt(group_no):
    qagent = find_qq_agent_by_no(qq_agents,group_no)
    prompt_state = qagent.agent.state.to_dict(change=False)
    prompt_state.update({'looptimes':0, 'augmented_prompt':''})
    result = qagent.agent.prompt.invoke(prompt_state).to_string()
    return await render_template('render_xml.html', xml_code=result, title=group_no+' Prompt')

@app.route('/get_qq_group_list')
async def get_qq_group_list():
    agent_links = {agent.no: f"/get_qq_prompt/{agent.no}" for agent in qq_agents}
    return await render_template('list_qqagents.html', links=agent_links)


@app.route('/get_doc/<doc_no>')
async def get_doc(doc_no):
    qagent = qq_agents[0]
    result = qagent.agent.state.docs_m.find_doc(doc_no,meta_on=False)
    return jsonify(result.to_dict())

@app.route('/list_doc')
async def list_doc():
    qagent = qq_agents[0]
    result = qagent.agent.state.docs_m.list(meta_on=False)
    return str(result)

tools = []

loop_funcs = [start_callback]

augmented_prompt = """Search the internet only Task or User request to."""
