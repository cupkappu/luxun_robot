from agents.percive_agent import percive_agent
import asyncio
import json
import os

g_agent:percive_agent = None

def give_callback(agent: percive_agent):
    global g_agent
    g_agent = agent
    if os.getenv('SAVE_STATE_PATH',None) != None:
        if os.path.exists(os.getenv('SAVE_STATE_PATH')):
            with open(os.getenv('SAVE_STATE_PATH')) as f:
                data = f.read()
                print(data)
                g_agent.state.replace(**json.loads(data))

async def start_callback():
    while True:
        await asyncio.sleep(g_agent.looptime)
        with open(os.getenv('SAVE_STATE_PATH'), 'w') as f:
            state = g_agent.state.to_dict()
            state['current_memory_list'] = g_agent.state.current_memory_list
            state['note'] = g_agent.state.note
            f.write(json.dumps(state))

tools = {}

augmented_prompt = """"""