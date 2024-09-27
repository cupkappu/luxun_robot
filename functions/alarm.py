from agents.percive_agent import percive_agent, get_time
from typing import Annotated
from langchain.tools import tool
from typing import List
import asyncio
import time
from functions.qq import QQAgent

g_agent:percive_agent = None
qq_agents: List[QQAgent] = []

class AsyncAlarm:
    def __init__(self, user, callback: callable = None):
        self.user = user
        self.alarms = []
        self.countdowns = []
        self.callback = callback

    def set_alarm(self, hour, minute, message):
        print(f'Add alarm {hour}:{minute}')
        self.alarms.append((hour, minute, message))

    def set_countdown(self, seconds, message):
        print(f'Add countdown {seconds}s')
        self.countdowns.append((seconds, message))

    async def check_alarm(self):
        print(f'Alarm watchdog for {self.user} will active now.')
        while True:
            current_time = time.localtime()
            alarms_to_remove = []
            for alarm in self.alarms:
                if current_time.tm_hour == alarm[0] and current_time.tm_min == alarm[1]:
                    try:
                        if self.callback:
                            self.callback(alarm[2])
                    except Exception as e:
                        print(f"Error in alarm callback: {e}")
                    alarms_to_remove.append(alarm)
            for alarm in alarms_to_remove:
                self.alarms.remove(alarm)
            await asyncio.sleep(1)

    async def check_countdown(self):
        print(f'Countdown watchdog for {self.user} will active now.')
        while True:
            countdowns_to_update = []
            for countdown in self.countdowns:
                remaining_time, message = countdown
                if remaining_time <= 0:
                    try:
                        if self.callback:
                            self.callback(message)
                    except Exception as e:
                        print(f"Error in countdown callback: {e}")
                else:
                    countdowns_to_update.append((remaining_time - 1, message))
            self.countdowns = countdowns_to_update
            await asyncio.sleep(1)

    async def loop(self):
        await asyncio.gather(
            self.check_alarm(),
            self.check_countdown()
        )

def callback_factory(agent:percive_agent):
    def warpper(message):
        print(f"Time Count task over, adding perceive into {str(agent.metadata)} perceives.")
        agent.perceives.append({"Alarm":message+get_time()})
        agent.enable = True
    return warpper

def tool_factory(alarms:AsyncAlarm):
    @tool
    def add_alarm(hour: Annotated[int, 'The hour of the alarm you want to set.'], 
                   minute: Annotated[int, 'The minute of the alarm you want to set.'], 
                   message: Annotated[str, 'The message when alarm active you want to let you notice.']):
        """Use add_alarm to add an alarm with a determined time. """
        print(f"setting {str(alarms.user)}'s alarm.")
        alarms.set_alarm(hour,minute,message)
        return "Alarm setted."
    @tool
    def add_countdown(seconds: Annotated[int, 'The seconds of the countdown you want to set.'], 
                   message: Annotated[str, 'The message when your countdown finished you want to let you notice.']):
        """Use add_countdown to add a countdown."""
        print(f"setting {str(alarms.user)}'s countdown.")
        alarms.set_countdown(seconds,message)
        return "Countdown seted."
    return [add_alarm, add_countdown]

alarms: List[AsyncAlarm] = []

def give_callback(agent: percive_agent, **kwargs):
    global g_agent, qq_agents,alarms,loop_funcs
    g_agent = agent
    qq_agents = kwargs.get('functions.qq',[])
    alarms = []
    for i in qq_agents:
        alarm = AsyncAlarm(i.agent.metadata['group'], callback_factory(i.agent))
        alarms.append(alarm)
        i.agent.add_tools(tool_factory(alarm))
    loop_funcs = [i.check_alarm for i in alarms] + [i.check_countdown for i in alarms]

tools = []
loop_funcs = []

augmented_prompt = """
Use add_alarm to add an alarm with a determined time. 
Use add_countdown to add a countdown."""
