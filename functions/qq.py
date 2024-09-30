import requests
import websockets
import os
from agents.percive_agent import percive_agent,State
from typing import Annotated, List,Dict
import json
from prompts.qq import qq_prompt,init_query
import re

g_agent:percive_agent = None

class QQAgent:
    no: str
    type: str
    agent: percive_agent
    def __init__(self, no:str, type:str, agent:percive_agent):
        self.no = no
        self.type = type
        self.agent = agent

qq_agents: List[QQAgent]
qq_states: Dict[str,State]

def give_callback(agent: percive_agent, **kwargs):
    global g_agent,qq_agents,loop_funcs, qq_states
    g_agent = agent
    qq_agents = [qq_perceiver_init(i, msg_type = 'group',) for i in id_list]
    loop_funcs = [start_callback] + [i.agent.loop for i in qq_agents]
    print([i.agent.metadata for i in qq_agents])
    return qq_agents

id_list = os.environ['QQ_GROUP_ID_LIST'].split(',')

def qq_perceiver_init(no: str, msg_type: str,):
    metadata = {msg_type:no,'category':'chat','platform':'qq'}
    n_state = State(**init_query,llm=g_agent.llm,metadata=metadata,
                    db_info = {
                    'storage':os.getenv('QQ_DB_TYPE','memory'),
                    'db_uri': os.getenv('QQ_DB_URI',''),
                    'db_name': os.getenv('QQ_DB_NAME',''),
                    'table': os.getenv('QQ_DB_TABLE',''),
                    },)
    agent = percive_agent(
                n_state,
                prompt=qq_prompt,
                tools={},
                llm=g_agent.llm,
                metadata=metadata,
                enable_llm_stop_marker = False,
                enable = False,
                looptime = int(os.getenv('WORKFLOW_LOOPTIME',60)),
                callback_invoker=lambda reply:send_qq_msg(msg=reply, no=no, to_type=msg_type))
    return QQAgent(no= no,type=msg_type,agent=agent)

# @tool
def send_qq_msg(msg: Annotated[str, 'Message you want to send'],
          no: Annotated[str, 'Group or QQ Number(Must be number, Do not use variable) you want to send to'],
          to_type: Annotated[str, 'group or private you need to select']):
    """Send messages to QQ"""
    params={}
    if (to_type=='group'):
        idtype='group_id'
    if (to_type=='private'):
        idtype='user_id'
    params={
        'message_type': to_type,
        idtype: no,
        'message': msg
    }
    url = f"{os.environ['QQ_ONEBOT_HTTP_URL']}/send_msg"
    requests.get(url,params=params)
    return "Message Send."

def find_qq_agent_by_no(qq_agents:List[QQAgent],no: str) -> QQAgent:
    matching_agents = None
    for i in qq_agents:
        if i.no == no:
            matching_agents = i
    return matching_agents

async def start_callback():
    url = os.environ['QQ_ONEBOT_WS_URL']
    print('start connect to', url)
    async with websockets.connect(url) as websocket:
        await websocket.send("Hello, WebSocket!")
        while True:
            message = await websocket.recv()
            try:
                msg = json.loads(message)
                if msg['post_type'] == 'message':
                    await on_message(msg)
            except json.JSONDecodeError:
                print("Received message is not a valid JSON")
            except KeyError as e:
                print(f"Key {e} not found in message")

async def on_message(msg:dict):
    print(msg)
    if isinstance(msg,dict):
        if msg['post_type'] == 'message':
            if msg['message_type'] == 'group':
                if str(msg['group_id']) in id_list:
                    perceive = {f"QQ群組|群號{msg['group_id']}":{"Sender": msg['sender'], 'Content':re.sub(r'\[CQ:.*?\]', '', msg['message'])}}
                    print(perceive)
                    # g_agent.perceives.append(perceive)
                    qq_agent = find_qq_agent_by_no(qq_agents,str(msg['group_id'])).agent
                    qq_agent.perceives.append(perceive)
                    if str(msg['self_id']) in msg['message']:
                        qq_agent.enable = True
            if msg['message_type'] == 'private':
                perceive = {f"QQ私聊|QQ號{msg['sender']['user_id']}":{"Sender": msg['sender']['nickname'], 'Content':msg['message']}}
                print(perceive)
                # g_agent.perceives.append(perceive)

# tools = [send_qq_msg]

tools = []
loop_funcs = []

augmented_prompt = """"""