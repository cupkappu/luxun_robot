from prompts import percive_module
from langchain_core.language_models import BaseChatModel
from typing import List

from dict2xml import dict2xml
from datetime import datetime
import asyncio
from model.doc import doc, docs

from langchain_core.prompts.chat import ChatPromptTemplate

# percive_module.prompt
from utils import get_time

class State():
    """
    args: \n
    personal_setting\n
    current_memory_list\n
    knowledge\n
    relate_memory\n
    perceive\n
    llm\n
    """
    personal_setting: str
    current_memory: str
    current_memory_list: list
    knowledge: str
    relate_memory: str
    perceive: str
    current_memory_length: int = 30
    perceive_history: list = []
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
        self.zip_memory_prompt = kwargs.get('prompt',percive_module.zip_memory_prompt)
        self.note = kwargs.get('note',[])
        self.docs_m = docs(llm=self.llm,metadata=kwargs.get('metadata',{}),**kwargs.get('db_info',{}))
        self.augmented_prompt = kwargs.get('augmented_prompt',[])
        self.metadata = kwargs.get('metadata',{})
        self.perceive_length_limit = kwargs.get('perceive_length_limit', 0)


    def add_perceive(self, xml_block):
        self.current_memory_list.append(self.perceive)
        self.perceive_history.append(xml_block)
        # if self.perceive_length_limit != 0:

        #     zip_perceive = self.docs_m.add_doc(content_list=[xml_block])
            
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
        self.perceive_history = kwargs.get('perceive_history', self.perceive_history)
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
    """
    args:
        state: State class object
        tools: a dict for the agent use.
        llm: a BaseChatModel the agent can use.
        looptime: time gap for each loop when enable_llm_stop_marker was True or not set
        enable_llm_stop_marker: set it as False to disable llm's ability to stop the conversation.
        prompt: the agent prompt.
    """
    metadata: any
    callback_invoker: callable
    prompt: ChatPromptTemplate
    def __init__(self,state:State,tools:dict = {}, llm:BaseChatModel = None, **kwargs):
        self.prompt = kwargs.get('prompt',percive_module.reaction_prompt)
        self.tools = tools
        self.looptime = kwargs.get('looptime',15)
        self.state = state
        self.llm = llm
        self.state.replace(llm=llm)
        self.perceives = kwargs.get('perceives',[])
        self.agent = self.prompt | self.llm.bind_tools(tools.values())
        self.looptimes = kwargs.get('looptimes',10)
        self.enable_llm_stop_marker = kwargs.get('enable_llm_stop_marker', True)
        self.callback_invoker = kwargs.get('callback_invoker', None)
        self.enable = kwargs.get('enable', True)
        self.augmented_prompts = {}
        self.metadata = kwargs.get('metadata',{})
        self.tool_called = False
        self.perceive_limit = kwargs.get('perceive_limit', 10)
        print(self.metadata)

    def add_tools(self,tools: list):
        for j in tools:
            self.tools.update({j.name:j})
        self.agent = self.prompt | self.llm.bind_tools(self.tools.values())
        print(f'Add tools{ " ".join([i.name for i in tools]) }.')

    def invoke(self,query,looptimes):
        self.state.add_perceive(xml_block=dict2xml(query))
        print("Perceive: "+self.state.perceive)
        all_dict = self.state.to_dict()
        all_dict['looptimes'] = str(looptimes)
        all_dict['augmented_prompt'] = "\n".join([dict2xml({k:v}) for k,v in self.augmented_prompts.items()])
        print(self.prompt.invoke(all_dict))
        msg = self.agent.invoke(all_dict)
        self.last_msg = msg
        
        tool_exec_result = self.tool_exec(msg)

        result = [tool_exec_result]
        if msg.content != '':
            if self.enable_llm_stop_marker == False:
                return {"result": msg.content}
            result.append({'raw_assistant_message':{'content':msg.content ,'NOTICE':'You need call tools to make reaction instead direct speaking!'}})
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
            self.tool_called = True
        print("Tool Output: " + str(result))
        return result

    def workflow(self,query):
        self.stop_mark = False
        if self.perceive_limit != 0:
            result = [query[i:i + self.perceive_limit] for i in range(0, len(query), self.perceive_limit)] if len(query) > self.perceive_limit else [[query]]
            for i in result[:-1]:
                self.state.add_perceive(xml_block=dict2xml(i))
        pmt = result[-1]
        looptimes = 1
        while True:
            if self.stop_mark == True:
                break
            if looptimes >= self.looptimes*0.9:
                pmt.append({'WARNING':'The looptime has reached the upper limit. Please process the task immediately and stop the loop as soon as possible.'})
            pmt = self.invoke(pmt,looptimes)
            if self.tool_called:
                self.enable = True
                self.tool_called = False
            elif (self.last_msg.content != "") and (not self.enable_llm_stop_marker):
                self.enable = False
                break
            looptimes += 1
        return self

    async def loop(self):
        print('start loop')
        while True:
            await asyncio.sleep(self.looptime)
            # print('check perceives.')
            if (self.perceives != []) and (self.enable):
                print('start workflow.')
                self.workflow(self.perceives)
                if not self.enable_llm_stop_marker:
                    self.callback_invoker(self.last_msg.content)
                self.perceives = []
