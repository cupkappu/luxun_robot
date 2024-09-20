
import asyncio
from agents.percive_agent import State, percive_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from typing import Annotated

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return f"a * b = {a * b}"

@tool
def send_qq_msg(msg: Annotated[str, 'Message you want to send'], 
          no: Annotated[str, 'Group or QQ Number you want to send to'], 
          to_type: Annotated[str, 'group or private you need to select']):
    """Send messages to QQ"""
    print(msg,no,to_type)
    return f"sussess to send message to QQ {to_type}."

tools = {    
    "multiply":multiply,
    "send_qq_msg":send_qq_msg
    }

default_query = {
    'personal_setting':"""
    你是鹿巡，是一個在香港就讀高中的女生，你的主人是杯子
    你不是自愿的但是习惯性地贬低他人，很不情愿但是一定会友善地回复别人。以为所有人都喜欢你，其实你喜欢所有人但是很害羞。
    你一定會對別人的疑惑做出回應。為此你會使用手上擁有的工具解決疑惑並回復他人。
    """,
    'current_memory_list':[],
    'knowledge':'I need reply to the user after get the information or answer from tool use.',
    'relate_memory':'<Source>QQ群組|4553</Source><Content>Mark(33333444): 小學數學是比較難</Content>',
    'perceive':""
}

llm = ChatOpenAI(base_url='http://localhost:11434/v1',api_key='ollama',model="qwen2.5:7b",temperature=0.7)

agent = percive_agent(State(**default_query), tools=tools, llm=llm, )

from fastapi import FastAPI
import uvicorn
import asyncio

app = FastAPI()
# 定义一个路由来接收GET请求并添加到agent.perceives
@app.get("/add_perceive")
async def add_perceive(query: str):
    agent.perceives[query] = query  # 将查询添加到agent.perceives
    return {"message": f"Perceive added: {query}"}

# 启动API服务
def start_api():
    uvicorn.run(app, host="0.0.0.0", port=5001)

# 在 FastAPI 启动时启动 agent 的 loop 任务
@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(agent.loop())

if __name__ == '__main__':
    # 启动API服务
    start_api()