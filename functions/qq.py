import requests
import websockets
import os
from agents.percive_agent import percive_agent,State
from typing import Annotated, List,Dict
import json
from prompts.qq import qq_prompt,init_query
import re
from .func_lib.qq_utils import process_cq
from agents.qq_contral import cmd_processer,cmd

g_agent:percive_agent = None

class QQAgent:
    no: str
    type: str
    agent: percive_agent
    def __init__(self, no:str, type:str, agent:percive_agent, cmd_controller: cmd_processer):
        self.no = no
        self.type = type
        self.agent = agent
        self.cmd_controller = cmd_controller

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

def qq_perceiver_init(no: str, msg_type: str,cmds:Dict[str,cmd] = {}) -> QQAgent:
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
    agent.augmented_prompts['qq'] = augmented_prompt
    cmd_controller = cmd_processer(cmds,agent=agent)
    return QQAgent(no= no,type=msg_type,agent=agent,cmd_controller=cmd_controller)

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
                    QQ_agent = find_qq_agent_by_no(qq_agents,str(msg['group_id']))
                    qq_agent = QQ_agent.agent
                    print(msg['message'].split(' ')[0].split('!')[1])
                    if msg['message'].split(' ')[0].split('!')[1] in list(QQ_agent.cmd_controller.cmds.keys()) + ['help']:
                        cmd_ctrl = QQ_agent.cmd_controller
                        result = cmd_ctrl.process(msg['message'])
                        send_qq_msg(msg=result, no=msg['group_id'], to_type='group')
                    perceive = {
                        f"QQ群組|群號{msg['group_id']}":{
                            "Sender": msg['sender'], 
                            'Content':re.sub(r'\[CQ:.*?\]', '', msg['message']),
                            'CQ': await process_cq(re.findall(r'\[CQ:.*?\]',msg['message']))
                        },
                        'speacial':{
                            'CQ': await process_cq(re.findall(r'\[CQ:.*?\]',msg['message']),img_llm = False)
                        }
                    }
                    print(perceive[f"QQ群組|群號{msg['group_id']}"])
                    # g_agent.perceives.append(perceive)
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

augmented_prompt = """There are a few points to pay attention to messages sent in QQ:
1. <CQ> The content in the label belongs to special information
2. If you want to be someone, please include [CQ:at,qq=(QQ Number)], like[CQ:at,qq=1234567](without spaces) in the reply, that is, you can AT.
3. The content contained in <user_id> is the QQ number of the message content sender"""