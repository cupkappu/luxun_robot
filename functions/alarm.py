from agents.percive_agent import percive_agent
from typing import Annotated
from langchain.tools import tool
from typing import List
import asyncio
import time

g_agent:percive_agent = None
qq_agents: List[percive_agent] = []

class AsyncAlarm:
    def __init__(self, user):
        self.user = user
        self.alarms = []
        self.countdowns = []

    async def set_alarm(self, hour, minute, callback):
        print(f'Add alarm {hour}:{minute}')
        self.alarms.append((hour, minute, callback))

    async def set_countdown(self, seconds, callback):
        print(f'Add countdown {seconds}s')
        self.countdowns.append((seconds, callback))

    async def check_alarm(self):
        while True:
            current_time = time.localtime()
            for alarm in self.alarms:
                if current_time.tm_hour == alarm[0] and current_time.tm_min == alarm[1]:
                    alarm[2](self.user)
                    self.alarms.remove(alarm)
            await asyncio.sleep(1)

    async def check_countdown(self):
        while self.countdowns:
            for i in range(len(self.countdowns)):
                remaining_time = self.countdowns[i][0]
                if remaining_time <= 0:
                    self.countdowns[i][1](self.user)
                    self.countdowns.remove(self.countdowns[i])
                else:
                    self.countdowns[i] = (remaining_time - 1, self.countdowns[i][1])
            await asyncio.sleep(1)  # 每秒更新一次倒計時

    async def loop(self):
        await asyncio.gather(
            self.check_alarm(),
            self.check_countdown()
        )

alarms: List[AsyncAlarm]

def give_callback(agent: percive_agent, in_qq_agents = []):
    global g_agent, qq_agents,alarms
    g_agent = agent
    qq_agents = in_qq_agents
    alarms = [AsyncAlarm(i.metadata['group']) for i in qq_agents]


tools = []
loop_funcs = [i.loop for i in alarms]

augmented_prompt = """"""