from quart import Quart, jsonify, request
from agents.percive_agent import percive_agent
from functions.qq import find_qq_agent_by_no, QQAgent
from typing import List

g_agent:percive_agent = None
qq_agents: List[QQAgent]

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
    result = qagent.agent.prompt.invoke(prompt_state).to_string()
    return render_page(result)

def render_page(content:str):
    return f"""
    <style>
        textarea {{
            width: 100%;
            height: 100%; /* 根据需要调整高度 */
            resize: both; /* 允许用户调整大小 */
            box-sizing: border-box; /* 确保内边距和边框不会增加元素的总宽度 */
        }}
    </style>
    <textarea readonly>{content}</textarea>"""

@app.route('/get_doc/<doc_no>')
async def get_doc(doc_no):
    qagent = qq_agents[0]
    result = qagent.agent.state.docs_m.find_doc(doc_no,meta_on=False)
    return render_page(jsonify(result.to_dict()))

@app.route('/list_doc')
async def list_doc():
    qagent = qq_agents[0]
    result = qagent.agent.state.docs_m.list(meta_on=False)
    return render_page(jsonify(result))

tools = []

loop_funcs = [start_callback]

augmented_prompt = """Search the internet only Task or User request to."""