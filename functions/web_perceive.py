from quart import Quart, jsonify, request
from agents.percive_agent import percive_agent

g_agent:percive_agent = None

def give_callback(agent: percive_agent):
    global g_agent
    g_agent = agent

app: Quart = Quart(__name__)

async def start_callback():
    config = {"host": "0.0.0.0", "port": 5000, "debug": False}
    await app.run_task(**config)

@app.route('/add_perceive', methods=['POST'])
async def add_perceive():
    json_data = await request.get_json()
    g_agent.perceives.append(json_data)
    return jsonify({"message": f"Perceive added: {json_data}"})

tools = {}