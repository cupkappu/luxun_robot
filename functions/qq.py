import requests
import websockets
import os
from agents.percive_agent import percive_agent
from langchain.tools import tool
from typing import Annotated
import json

g_agent:percive_agent = None

def give_callback(agent: percive_agent):
    global g_agent
    g_agent = agent

id_list = os.environ['QQ_GROUP_ID_LIST'].split(',')

@tool
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
                    perceive = {f"QQ群組|群號{msg['group_id']}":{"Sender": msg['sender'], 'Content':msg['message']}}
                    print(perceive)
                    g_agent.perceives.append(perceive)
            if msg['message_type'] == 'private':
                perceive = {f"QQ私聊|QQ號{msg['sender']['user_id']}":{"Sender": msg['sender']['nickname'], 'Content':msg['message']}}
                print(perceive)
                g_agent.perceives.append(perceive)

tools = {"send_qq_msg":send_qq_msg}