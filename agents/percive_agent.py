from prompts import percive_module
from langchain_core.language_models import BaseChatModel
from typing import Annotated, Dict
from dict2xml import dict2xml
from langchain.tools import tool
from datetime import datetime
import asyncio

# percive_module.prompt

@tool
def stop_marker(stop_mark: Annotated[bool, 'Mark as true to stop.']) -> str:
    """Set the stop mark as true when you don't have more to do."""
    if stop_mark == True:
        return "<STOP_MARK />"
    return ""

class State():
    personal_setting: str
    current_memory: str
    current_memory_list: list
    knowledge: str
    relate_memory: str
    perceive: str
    current_memory_length: int = 30
    perceive_history: list
    llm: BaseChatModel

    def __init__(self, *args, **kwargs):
        self.personal_setting = kwargs['personal_setting']
        self.current_memory_list = kwargs['current_memory_list']
        self.knowledge = kwargs['knowledge']
        self.relate_memory = kwargs['relate_memory']
        self.perceive = kwargs['perceive']
        self.current_memory_length = kwargs.get('current_memory_length',self.current_memory_length)
        self.llm = kwargs.get('llm',None)
        self.zip_memory_prompt = percive_module.zip_memory_prompt

    def add_perceive(self, xml_block):
        self.current_memory_list.append(self.perceive)
        self.perceive = xml_block + f'<Time>{datetime.now().strftime("%Y-%m-%d %H:%M")}</Time>'
        memory_length = len(self.current_memory_list)
        memory_limit = int(self.current_memory_length*0.9)
        memory_cache_length = int(self.current_memory_length*0.7)
        if memory_length >= memory_limit:
            cache=self.current_memory[-(memory_length-memory_cache_length)]
            invoker = self.zip_memory_prompt|self.llm
            zip_memory = invoker.invoke(
                
                    self.write_current_memory(cache).to_dict(),
                ).content
            self.current_memory_list = [zip_memory]+self.current_memory_list[memory_cache_length]
        self.write_current_memory(self.current_memory_list)
        return self

    def replace(self, **kwargs):
        self.personal_setting = kwargs.get('personal_setting', self.personal_setting)
        self.current_memory_list = kwargs.get('current_memory', self.current_memory_list)
        self.knowledge = kwargs.get('knowledge', self.knowledge)
        self.relate_memory = kwargs.get('relate_memory', self.relate_memory)
        self.perceive = kwargs.get('perceive', self.perceive)
        self.current_memory_length = kwargs.get('current_memory_length',self.current_memory_length)
        self.llm = kwargs.get('llm',self.llm)
        return self

    def write_current_memory(self,memory_list:list = None):
        self.current_memory = "\n".join(memory_list if memory_list != None else self.current_memory_list)
        return self
    
    def to_dict(self):
        return {
            'personal_setting':self.personal_setting,
            'current_memory':self.write_current_memory().current_memory,
            'knowledge':self.knowledge,
            'relate_memory':self.relate_memory,
            'perceive':self.perceive,
        }

class percive_agent:
    def __init__(self,state:State,tools:dict = {}, llm:BaseChatModel = None, **kwargs):
        self.prompt = percive_module.reaction_prompt
        self.tools = tools
        self.tools["stop_marker"] =  stop_marker
        self.looptime = kwargs.get('looptime',15)
        self.state = state
        self.llm = llm
        self.state.replace(llm=llm)
        self.perceives = []
        self.agent = self.prompt | self.llm.bind_tools(tools.values())

    def invoke(self,query,looptimes):
        self.state.add_perceive(xml_block=dict2xml(query))
        print("Perceive: "+self.state.perceive)
        all_dict = self.state.to_dict()
        all_dict['looptimes'] = str(looptimes)
        msg = self.agent.invoke(all_dict)
        self.last_msg = msg
        tool_exec_result = self.tool_exec(msg)
        if 'stop_marker' in tool_exec_result['Content'].keys():
            self.stop_mark = True
        return tool_exec_result

    def tool_exec(self, msg):
        result = {'Content':{}}
        for tool_call in msg.tool_calls:
            selected_tool = self.tools[tool_call["name"].lower()]
            tool_output = selected_tool.invoke(tool_call["args"])
            result['Source'] = "ToolUse"
            result['Content'][tool_call["name"]] = {
                'input_args':tool_call["args"],
                'output':tool_output}
        print("Tool Output: " + str(result))
        return result

    def workflow(self,query):
        self.stop_mark = False
        pmt = query
        looptimes = 1
        while True:
            if self.stop_mark == True:
                break
            pmt = self.invoke(pmt,looptimes)
            looptimes += 1
        return self

    async def loop(self):
        print('start loop')
        while True:
            await asyncio.sleep(self.looptime)
            print('check perceives.')
            if self.perceives != []:
                print('start workflow.')
                self.workflow(self.perceives)
                self.perceives = []