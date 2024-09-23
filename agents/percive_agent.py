from prompts import percive_module
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field
from typing import Annotated, List, Dict,Optional
from langchain_core.output_parsers import JsonOutputParser

from dict2xml import dict2xml
from langchain.tools import tool
from datetime import datetime
import asyncio
import uuid

# percive_module.prompt

@tool
def stop_marker(stop_mark: Annotated[bool, 'Mark as true to stop.']
                ) -> str:
    """Set the stop mark as true when you don't have more to do."""
    if stop_mark == True:
        return "<STOP_MARK />"
    return "<STOP_MARK />"

def get_time():
    return f'<Time>{datetime.now().strftime("%Y-%m-%d %H:%M")}</Time>'


class sum_format(BaseModel):
    summary: str = Field(description="The summary of your current memory.")

class doc():
    doc: List
    uuid: str
    summary: str
    time: str
    def __init__(self,doc: List, llm: BaseChatModel=None, summary: str = ''):
        self.doc = doc
        self.uuid = uuid.uuid4()
        if summary == '':
            sumer = percive_module.sum_prompt | llm.bind(response_format={"type": "json_object"}) | JsonOutputParser(pydantic_object=sum_format)
            self.summary = sumer.invoke({'content':self.__str__()})['summary']
            print("Doc add:" + self.summary)
        else:
            self.summary = summary
        self.time = get_time()
    def __str__(self) -> str:
        result = ""
        for i in self.doc:
            if isinstance(i, str):
                result += i+'\n'
            elif isinstance(i, doc):
                result += i.get_summary()
        return result
    def get_summary(self) -> str:
        return f"<DOC><UUID>{self.uuid}</UUID><SUMMARY>{self.summary}</SUMMARY>{self.time}</DOC>\n"

class docs:
    docs: List[doc]
    def __init__(self, llm: BaseChatModel, docs: List[doc] = []):
        self.docs = docs
        self.llm = llm
    def find_doc(self, uuid:str) -> doc:
        for i in self.docs:
            if str(i.uuid) == uuid:
                return i
        return None
    def add_doc(self, content_list:list):
        c_doc = doc(doc=content_list,llm=self.llm)
        self.docs.append(c_doc)
        return c_doc

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
    note: list = []
    docs_m: docs

    def __init__(self, *args, **kwargs):
        self.personal_setting = kwargs['personal_setting']
        self.current_memory_list = kwargs['current_memory_list']
        self.knowledge = kwargs['knowledge']
        self.relate_memory = kwargs['relate_memory']
        self.perceive = kwargs['perceive']
        self.current_memory_length = kwargs.get('current_memory_length',self.current_memory_length)
        self.llm = kwargs.get('llm',None)
        self.zip_memory_prompt = percive_module.zip_memory_prompt
        self.note = kwargs.get('note',[])
        self.docs_m = docs(llm=self.llm)

    def add_perceive(self, xml_block):
        self.current_memory_list.append(self.perceive)
        self.perceive = xml_block + get_time()
        memory_length = len(self.current_memory_list)
        memory_limit = int(self.current_memory_length*0.9)
        memory_cache_length = int(self.current_memory_length*0.7)
        if memory_length >= memory_limit:
            cache=self.current_memory_list[:(memory_length-memory_cache_length)]
            print('Zip Cache:\n',cache)
            zip_memory = self.docs_m.add_doc(content_list=cache)
            print(zip_memory)
            self.current_memory_list = [zip_memory]+self.current_memory_list[memory_length-memory_cache_length:]
        self.write_current_memory()
        return self

    def replace(self, **kwargs):
        self.personal_setting = kwargs.get('personal_setting', self.personal_setting)
        self.current_memory_list = kwargs.get('current_memory_list', self.current_memory_list)
        self.knowledge = kwargs.get('knowledge', self.knowledge)
        self.relate_memory = kwargs.get('relate_memory', self.relate_memory)
        self.perceive = kwargs.get('perceive', self.perceive)
        self.current_memory_length = kwargs.get('current_memory_length',self.current_memory_length)
        self.llm = kwargs.get('llm',self.llm)
        self.note = kwargs.get('note',self.note)
        self.augmented_prompt = {}
        return self

    def write_current_memory(self,memory_list:list = None):
        memory_list = memory_list if memory_list != None else self.current_memory_list
        self.current_memory = ''
        for i in memory_list:
            if isinstance(i, doc):
                self.current_memory += '\n' + i.get_summary()
            if isinstance(i, str):
                self.current_memory += '\n' + i
        return self
    
    def to_dict(self):
        return {
            'personal_setting':self.personal_setting,
            'current_memory':self.write_current_memory().current_memory,
            'knowledge':self.knowledge,
            'relate_memory':self.relate_memory,
            'perceive':self.perceive,
            'note': "\n".join([f"<NOTE_UNIT>{dict2xml(i)}</NOTE_UNIT>" for i in self.note])
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
        self.agent = self.prompt | self.llm.bind_tools(tools.values(),tool_choice="any")
        self.looptimes = kwargs.get('looptimes',10)

    def invoke(self,query,looptimes):
        self.state.add_perceive(xml_block=dict2xml(query))
        print("Perceive: "+self.state.perceive)
        all_dict = self.state.to_dict()
        all_dict['looptimes'] = str(looptimes)
        all_dict['augmented_prompt'] = "\n".join(self.augmented_prompts)
        msg = self.agent.invoke(all_dict)
        self.last_msg = msg
        print(msg)
        tool_exec_result = self.tool_exec(msg)
        if 'stop_marker' in tool_exec_result['Content'].keys():
            self.stop_mark = True
        result = tool_exec_result
        if msg.content != '':
            result.update({'raw_assistant_message':msg.content ,'NOTICE':'You need call tools to make reaction instead direct speaking!'})
        return result

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
            if looptimes >= self.looptimes*0.9:
                pmt.append({'WARNING':'The looptime has reached the upper limit. Please process the task immediately and stop the loop as soon as possible.'})
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
                