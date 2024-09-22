from mem0 import memory
from prompts import mem_agent
from langchain_core.language_models import BaseChatModel
from typing import Annotated, Dict, Optional,List
from dict2xml import dict2xml
from langchain.tools import tool
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod

@tool
def relevent_doc(doc_number:Annotated[List[int], 'The document number you want to select']):
    """Select 3 most relevent documents."""
    return doc_number

class basedoc(ABC):
    content: str
    is_collection: bool
    @abstractmethod
    def get_doc():
        pass
    @abstractmethod
    def next():
        pass

class doc(basedoc):
    def __init__(self,content:str|List[basedoc],is_collection: bool,summary: Optional[str]):
        self.content = content
        self.is_collection = is_collection
        if is_collection:
            self.summary = summary
    def get_doc(self):
        if self.is_collection:
            return self.summary
        else:
            return self.content
    def next(self):
        if self.is_collection:
            return self.content
        else:
            return [doc(self.content,False)]

class zip_mem:
    def __init__(self,llm:BaseChatModel = None, doc_list: List[doc] = None):
        self.llm = llm.bind_tools([relevent_doc])
        self.doc_list = doc_list
        self.prompt = mem_agent.find_doc_prompt
    def zip(self):
        zip_agent = self.prompt | self.llm
        # self.summary = 

# class mem_agent:
#     def __init__(self, llm:BaseChatModel = None, **kwargs):
#         pass
