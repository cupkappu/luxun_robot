from agents.percive_agent import percive_agent
from typing import Annotated
from langchain.tools import tool
import asyncio
import os
from textwrap import dedent

g_agent:percive_agent = None

def give_callback(agent: percive_agent, **kwargs):
    global g_agent
    g_agent = agent

async def start_callback():
    while True:
        await asyncio.sleep(g_agent.looptime)
        g_agent.augmented_prompts[__name__] = augmented_prompt.format(**prompt_vars)
        
prompt_vars = {'current_task':''}

@tool
def stop_marker(stop_mark: Annotated[bool, 'Mark as true to stop.']
                ) -> str:
    """Set the stop mark as true when you don't have more to do."""
    g_agent.stop_mark = stop_mark
    global prompt_vars
    prompt_vars['current_task'] = ''
    if stop_mark == True:
        g_agent.stop_mark = True
        return "<STOP_MARK_IS_TRUE />"
    return "<STOP_MARK_IS_FALSE />"

@tool
def set_current_task(task: Annotated[str, 'The task you need to do based on the instruction.']
                ) -> str:
    """Set a task as your current task you need to do. e.g. refer the question to somebody with some function and params."""
    global prompt_vars
    if prompt_vars['current_task'] == '':
        prompt_vars['current_task'] = task
        print(prompt_vars['current_task'])
        return f"Set {task} as the current task successfully."
    else:
        return "Already have a curren task! Please finish the curren task or stop your process."

tools = [stop_marker,set_current_task]

loop_funcs = [start_callback]

augmented_prompt = dedent("""
    <CURRENT_TASK>
    {current_task}
    </CURRENT_TASK>
    <TODO>
    What surround by <CURRENT_TASK> is your current task you need to finish. 
    If it is blank, call set_current_task to add a need-todo task as current task with necessary information like the state you might be used.
    For example: answer XXX(000000)'s [theme] problem.
    If all things done, call stop_marker.
    </TODO>
""")