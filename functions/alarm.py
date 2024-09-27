from agents.percive_agent import percive_agent
from typing import Annotated
from langchain.tools import tool
from typing import List
import asyncio
import time

g_agent:percive_agent = None
qq_agents: List[percive_agent] = []

class AsyncAlarm:
    def __init__(self, user, callback: callable = None):
        self.user = user
        self.alarms = []
        self.countdowns = []
        self.callback = callback

    async def set_alarm(self, hour, minute, message):
        print(f'Add alarm {hour}:{minute}')
        self.alarms.append((hour, minute, message))

    async def set_countdown(self, seconds, message):
        print(f'Add countdown {seconds}s')
        self.countdowns.append((seconds, message))

    async def check_alarm(self):
        while True:
            current_time = time.localtime()
            for alarm in self.alarms:
                if current_time.tm_hour == alarm[0] and current_time.tm_min == alarm[1]:
                    self.callback(alarm[2])
                    self.alarms.remove(alarm)
            await asyncio.sleep(1)

    async def check_countdown(self):
        while self.countdowns:
            for i in range(len(self.countdowns)):
                remaining_time = self.countdowns[i][0]
                if remaining_time <= 0:
                    self.callback(self.countdowns[i][1])
                    self.countdowns.remove(self.countdowns[i])
                else:
                    self.countdowns[i] = (remaining_time - 1, self.countdowns[i][1])
            await asyncio.sleep(1)  # 每秒更新一次倒計時

    async def loop(self):
        await asyncio.gather(
            self.check_alarm(),
            self.check_countdown()
        )

def callback_factory(agent:percive_agent):
    def warpper(message):
        agent.perceives.append({"Alarm":message})
        agent.enable = True
    return warpper

def tool_factory(alarms:AsyncAlarm):
    @tool
    def add_alarm(hour: Annotated[int, 'The hour of the alarm you want to set.'], 
                   minute: Annotated[int, 'The minute of the alarm you want to set.'], 
                   message: Annotated[str, 'The message when alarm active you want to let you notice.']):
        """Set a alarm to notice you in at the setted time moment."""
        alarms.set_alarm(hour,minute,message)
        return "Alarm setted."
    @tool
    def add_countdown(seconds: Annotated[int, 'The seconds of the countdown you want to set.'], 
                   message: Annotated[str, 'The message when your countdown finished you want to let you notice.']):
        """Set a countdown to notice you after the second."""
        alarms.set_countdown(seconds,message)
        return "Countdown seted."
    return [add_alarm, add_countdown]

alarms: List[AsyncAlarm] = []

def give_callback(agent: percive_agent, in_qq_agents = []):
    global g_agent, qq_agents,alarms
    g_agent = agent
    qq_agents = in_qq_agents
    alarms = []
    for i in qq_agents:
        alarm = AsyncAlarm(i.metadata['group'], callback_factory(i))
        alarms.append(alarm)
        i.add_tools(tool_factory(alarm))

tools = []
loop_funcs = [i.check_alarm for i in alarms] + [i.check_countdown for i in alarms]

augmented_prompt = """Use add_alarm to add an alarm with a determined time. Use add_countdown to add an countdown."""