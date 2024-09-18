import requests
import websocket
import os

async def send_message(reply,id,type='group'):
    params={}
    if (type=='group'):
        idtype='group_id'
    if (type=='private'):
        idtype='user_id'
    params={
        'message_type': type,
        idtype: id,
        'message': reply
    }
    url = f"{os.getenv('QQ_ONEBOT_HTTP_URL')}/send_msg" #这里要加上http://，不然会报错
    return requests.get(url,params=params)

async def get_notice(on_message):
    ws = websocket.WebSocketApp("ws://10.66.35.155:27636",
                            on_message=on_message,)
    ws.on_open = lambda ws:ws.send("Hello, WebSocket!")
    ws.run_forever()

