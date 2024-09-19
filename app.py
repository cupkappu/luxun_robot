from dotenv import load_dotenv

load_dotenv()

import asyncio
from agents.percive_agent import State, percive_agent
from llm import llm
from prompts.percive_module import test_query
import os
from functions import (qq,
                       web_perceive,
                       )

tools = {}

async def run_all_functions():
    func_modules = [
        web_perceive,
        qq,
    ]

    for i in func_modules:
        tools.update(i.tools)

    agent = percive_agent(State(**test_query), tools=tools, llm=llm, looptime = int(os.getenv('WORKFLOW_LOOPTIME',60)))

    [i.give_callback(agent) for i in func_modules]
    functions = [i.start_callback() for i in func_modules] + [agent.loop()]
    await asyncio.gather(*functions)

if __name__ == '__main__':
    asyncio.run(run_all_functions())