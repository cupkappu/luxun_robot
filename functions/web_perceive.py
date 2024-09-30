from quart import Quart, jsonify, request
from agents.percive_agent import percive_agent
from functions.qq import find_qq_agent_by_no, QQAgent
from typing import List

g_agent:percive_agent = None
qq_agents: List[percive_agent]

def give_callback(agent: percive_agent, **kwargs):
    global g_agent, qq_agents
    g_agent = agent
    qq_agents = kwargs['functions.qq']

app: Quart = Quart(__name__)

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
    prompt_state = qagent.agent.state.to_dict()
    prompt_state.update({'looptimes':0, 'augmented_prompt':''})
    result = "\n\n".join([i for i in qagent.agent.prompt.invoke(prompt_state)])
    return result

tools = []

loop_funcs = [start_callback]

augmented_prompt = """Search the internet only Task or User request to."""