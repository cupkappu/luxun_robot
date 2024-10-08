import uuid as uuidl
from langchain_core.language_models import BaseChatModel
from typing import List
from pydantic import BaseModel, Field
from prompts import percive_module
from langchain_core.output_parsers import JsonOutputParser
from .base_models import have_dict
from model.adapter import *
from utils import get_time
from .memorys import perceive_unit

class sum_format(BaseModel):
    summary: str = Field(description="The summary of your current memory.")

class doc(have_dict):
    doc: List
    uuid: str
    summary: str
    time: str
    def __init__(self,doc: List, uuid: str = str(uuidl.uuid4()), llm: BaseChatModel=None, summary: str = '',time:str = get_time(),doc_type:str ='default',**kwargs):
        self.doc = doc
        self.uuid = uuid
        self.type = doc_type
        if summary == '':
            sumer = percive_module.sum_prompt | llm.bind(response_format={"type": "json_object"}) | JsonOutputParser(pydantic_object=sum_format)
            self.summary = sumer.invoke({'content':self.__str__()})['summary']
            print("Doc add:" + self.summary)
        else:
            self.summary = summary
        self.time = time
    def __str__(self) -> str:
        result = ""
        if not isinstance(self.doc, doc):
            return str(self.doc)
        for i in self.doc:
            if isinstance(i, str):
                result += i+'\n'
            elif isinstance(i, doc):
                result += i.get_summary()
            else:
                result += str(i) + '\n'
        return result
    def get_summary(self) -> perceive_unit:
        return perceive_unit({'DOC':{'UUID':self.uuid,'SUMMARY':self.summary,'time':self.time}})
    def to_dict(self):
        return {
            'doc':self.doc,
            'uuid': self.uuid,
            'summary': self.summary,
            'time': self.time,
            'type': self.type
        }

class docs:
    storage: str
    def __init__(self, llm: BaseChatModel, docs: List[doc] = [], storage: str = 'memory', db_uri: str = '',db_name:str = '',table:str = '', metadata: dict = {}):
        if storage == 'memory':
            self.docs = docs
        else:
            self.metadata = metadata
            self.storage_driver = db_drivers[storage](db_uri=db_uri,db_name=db_name,table=table+'_doc',constructor=doc, metadata = self.metadata)
        self.storage = storage
        self.llm = llm
    def find_doc(self, uuid:str, meta_on = True) -> doc:
        if self.storage == 'memory':
            for i in self.docs:
                if str(i.uuid) == uuid:
                    return i
            return None
        return self.storage_driver.find_one(uuid, meta_on, llm=self.llm)
    def add_doc(self, content_list:list, doc_type:str = 'default'):
        c_doc = doc(doc=content_list,llm=self.llm,doc_type=doc_type)
        if self.storage == 'memory': self.docs.append(c_doc)
        else: self.storage_driver.save_one(c_doc)
        return c_doc
    def list_docs(self,fields:List[str] = ['uuid','summary'], meta_on:bool = True):
        result = self.storage_driver.list_all(fields=fields, meta_on = meta_on)
        return result
