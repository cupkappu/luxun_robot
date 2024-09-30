import uuid as uuidl
from langchain_core.language_models import BaseChatModel
from typing import List
from pydantic import BaseModel, Field
from prompts import percive_module
from langchain_core.output_parsers import JsonOutputParser
from datetime import datetime
from .base_models import have_dict
from model.adapter import *
from utils import get_time

class sum_format(BaseModel):
    summary: str = Field(description="The summary of your current memory.")

class doc(have_dict):
    doc: List
    uuid: str
    summary: str
    time: str
    def __init__(self,doc: List, uuid: str = str(uuidl.uuid4()), llm: BaseChatModel=None, summary: str = '',time:str = get_time()):
        self.doc = doc
        self.uuid = uuid
        if summary == '':
            sumer = percive_module.sum_prompt | llm.bind(response_format={"type": "json_object"}) | JsonOutputParser(pydantic_object=sum_format)
            self.summary = sumer.invoke({'content':self.__str__()})['summary']
            print("Doc add:" + self.summary)
        else:
            self.summary = summary
        self.time = time
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
    def to_dict(self):
        return {
            'doc':self.doc,
            'uuid': self.uuid,
            'summary': self.summary,
            'time': self.time
        }

class docs:
    storage: str
    def __init__(self, llm: BaseChatModel, docs: List[doc] = [], storage: str = 'memory', db_uri: str = '',db_name:str = '',table:str = '', metadata: dict = {}):
        if storage == 'memory':
            self.docs = docs
        else:
            self.storage_driver = db_drivers[storage](db_uri=db_uri,db_name=db_name,table=table,constructor=doc, metadata = metadata)
        self.storage = storage
        self.llm = llm
    def find_doc(self, uuid:str, meta_on = True) -> doc:
        if self.storage == 'memory':
            for i in self.docs:
                if str(i.uuid) == uuid:
                    return i
            return None
        return self.storage_driver.find_one(uuid, meta_on)
    def add_doc(self, content_list:list):
        c_doc = doc(doc=content_list,llm=self.llm)
        if self.storage == 'memory': self.docs.append(c_doc)
        else: self.storage_driver.save_one(c_doc)
        return c_doc
