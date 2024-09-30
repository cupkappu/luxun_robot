from agents.percive_agent import percive_agent, get_time
from typing import Annotated,List,Optional
from langchain.tools import tool
import asyncio
from datetime import datetime, timedelta
from functions.qq import QQAgent
import uuid

g_agent:percive_agent = None
qq_agents: List[QQAgent] = []

class AsyncAlarm:
    def __init__(self, user, callback: callable = None):
        self.user = user
        self.alarms = {}
        self.countdowns = []
        self.callback = callback

    def set_alarm(self, hour, minute, message,):
        print(f'Add alarm {hour}:{minute}')
        alarm_id = str(uuid.uuid4())
        self.alarms[alarm_id] = (hour, minute, message,)
        return alarm_id

    def set_countdown(self, seconds, message):
        print(f'Add countdown {seconds}s')
        self.countdowns.append((seconds, message))

    async def check_alarm(self):
        print(f'Alarm watchdog for {self.user} will active now.')
        while True:
            current_time = datetime.now()
            for alarm_id, (hour, minute, message,) in list(self.alarms.items()):
                if current_time.hour == hour and current_time.minute == minute:
                    try:
                        self.callback(message)
                        del self.alarms[alarm_id]
                    except Exception as e:
                        print(f"Error in alarm callback: {e}")
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

    def get_alarms(self):
        results = []
        for k, i in self.alarms.items():
            results.append({'id':k,'Time':f"{i[0]}:{i[1]}","message":i[2],"repeat_type":i[3],"repeat_value":i[4]})
        return results
    
    def remove_alarm(self, alarm_id):
        if alarm_id in self.alarms:
            del self.alarms[alarm_id]
            print(f'Alarm with ID {alarm_id} removed.')
        else:
            print(f'No alarm found with ID {alarm_id}.')

def callback_factory(agent:percive_agent):
    def warpper(message):
        print(f"Time Count task over, adding perceive into {str(agent.metadata)} perceives.")
        agent.perceives.append({"Alarm":message+get_time()})
        agent.enable = True
    return warpper

def tool_factory(alarms: AsyncAlarm):
    @tool
    def add_alarm(hour: Annotated[int, 'The hour of the alarm you want to set.'],
                   minute: Annotated[int, 'The minute of the alarm you want to set.'],
                   message: Annotated[str, 'The message to display when the alarm is triggered.'],):
        """
        Use add_alarm to add an alarm with a determined time and optional repetition.
        """
        print(f"Setting {str(alarms.user)}'s alarm.")
        alarm_id = alarms.set_alarm(hour, minute, message,)
        return f"Alarm {alarm_id} set."
    @tool
    def add_countdown(seconds: Annotated[int, 'The seconds of the countdown you want to set.'],
                       message: Annotated[str, 'The message to display when the countdown finishes.']):
        """
        Use add_countdown to add a countdown.
        """
        print(f"Setting {str(alarms.user)}'s countdown.")
        alarms.set_countdown(seconds, message)
        return "Countdown set."
    @tool
    def get_alarms() -> Annotated[List[dict], 'List of alarms']:
        """
        Use get_alarms to retrieve all set alarms.
        """
        return alarms.get_alarms()
    @tool
    def remove_alarm(alarm_id: Annotated[str, 'The unique identifier for the alarm to remove.']):
        """
        Use remove_alarm to remove a specific alarm by its ID.
        """
        print(f"Removing alarm with ID {str(alarm_id)} for {str(alarms.user)}.")
        alarms.remove_alarm(alarm_id)
        return f"Alarm {alarm_id} removed."
    return [add_alarm, add_countdown,get_alarms,remove_alarm]

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
