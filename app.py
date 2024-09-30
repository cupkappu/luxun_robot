# from dotenv import load_dotenv

# load_dotenv()

import asyncio
from agents.percive_agent import State, percive_agent
from llm import llm
from prompts.percive_module import test_query
import os

from functions import (
                    qq, 
                    save_state,
                    note_tools, 
                    web_perceive,
                    searxng,
                    task_manager,
                    alarm
                    )

tools = {}

async def run_all_functions():
    func_modules = [
        qq,
        web_perceive,
        searxng,
        save_state,
        note_tools,
        task_manager,
        alarm
    ]

    for i in func_modules:
        for j in i.tools:
            tools.update({j.name:j})

    agent = percive_agent(State(**test_query, llm=llm), tools=tools, llm=llm, looptime = int(os.getenv('WORKFLOW_LOOPTIME',60)))

    giver_tunnel = {}

    for i in func_modules:
        giver_tunnel.update({i.__name__:i.give_callback(agent, **giver_tunnel)})

    agent.augmented_prompts = dict(zip([i.__name__ for i in func_modules],[i.augmented_prompt for i in func_modules]))
    functions = [j() for i in func_modules for j in i.loop_funcs] # + [agent.loop()]
    await asyncio.gather(*functions)

if __name__ == '__main__':
    asyncio.run(run_all_functions())