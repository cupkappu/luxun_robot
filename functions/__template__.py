from agents.percive_agent import percive_agent

g_agent:percive_agent = None

def give_callback(agent: percive_agent):
    global g_agent
    g_agent = agent

async def start_api():
    pass

tools = {}