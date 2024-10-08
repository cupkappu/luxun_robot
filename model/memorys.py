from .base_models import have_dict
from typing import Union, List
from dict2xml import dict2xml
from .adapter import db_drivers
import uuid as uuidl
from utils import get_time
from datetime import datetime, timezone

class perceive_unit(have_dict):

    content: Union[str,dict]
    uuid: str

    def __init__(self, content:Union[str,dict],uuid: str = str(uuidl.uuid4()),**kwargs):
        self.content = content
        self.metadata = kwargs.get('metadata',{})
        self.time = get_time()
        self.uuid = uuid

    def __str__(self) -> str:
        if isinstance(self.content, str):
            return str(self.content)
        elif isinstance(self.content, dict):
            content = self.content.copy()
            if 'speacial' in content:
                del content['speacial']
            return dict2xml(content,newlines=False)
        return ""
    
    def to_dict(self) -> dict:

        return {
            'content': self.content,
            'time': self.time
        }

class perceive_group():

    perceives: List[perceive_unit]
    perceive_limit: int
    store_memory: callable

    def __init__(self, 
                 perceives:List[perceive_unit] = [], 
                 perceive_limit: int = 20, 
                 store_memory:callable = None,
                 storage: str = 'memory', 
                 db_uri: str = '',
                 db_name:str = '',
                 table:str = '', 
                 metadata: dict = {},**kwargs
                 ):
        self.perceives = perceives
        self.perceive_limit = perceive_limit
        self.store_memory = store_memory
        self.metadata = metadata
        if storage != 'memory':
            self.storage_driver = db_drivers[storage](
                db_uri=db_uri,
                db_name=db_name,
                table=table+'_perceive',
                constructor=perceive_unit,
                metadata = self.metadata)
    
    def get_perceive(self, change:bool = True) -> str:
        result = "\n".join([str(i) for i in self.perceives])
        if change:
            self.store_memory(self.perceives)
            self.perceives = []
        return result
    
    def isnull(self) -> bool:
        return self.perceives == []

    def __str__(self) -> str:
        result = "\n".join([str(i) for i in self.perceives])
        return result

    def append(self, content: Union[str, dict]):
        new_perceive = perceive_unit(content=content)
        self.perceives.append(new_perceive)
        self.storage_driver.save_one(new_perceive)
#        if self.store_memory is not None:
#            if len(self.perceives) > self.perceive_limit:
#                chunks = [self.perceives[i:i + self.perceive_limit] for i in range(0, len(self.perceives) - self.perceive_limit, self.perceive_limit)]
#                for chunk in chunks:
#                    try:
#                        self.store_memory(chunk)
#                    except Exception as e:
#                        print(f"?????????????????????: {e}")
#                self.perceives = self.perceives[-self.perceive_limit:]

class memory_list():

    memorys: List[perceive_unit]
    memory_limit: int = 30
    memory_zip_rate: float = 0.3
    zip_memory: callable

    def __init__(self, 
                 memorys: List[perceive_unit] = [], 
                 memory_limit:int = 30, 
                 zip_memory: callable = None, 
                 memory_zip_rate: float = 0.3,
                 storage: str = 'memory', 
                 db_uri: str = '',
                 db_name:str = '',
                 table:str = '', 
                 metadata: dict = {},**kwargs
                 ):
        self.memorys = memorys
        self.memory_limit = memory_limit
        self.zip_memory = zip_memory
        self.memory_zip_rate = memory_zip_rate
        self.metadata = metadata
        if storage != 'memory':
            self.storage_driver = db_drivers[storage](
                db_uri=db_uri,
                db_name=db_name,
                table=table+'_perceive',
                constructor=perceive_unit, 
                metadata = self.metadata)
            self.memorys = self.storage_driver.find_nums(nums = int(round(memory_limit*0.3)))

    def __str__(self) -> str:
        return "\n".join([str(i) for i in self.memorys])
    
    def append(self,content:perceive_unit):
        self.memorys.append(content)
        if self.zip_memory != None:
            if len(self.memorys) > self.memory_limit:
                willzip_memory = self.memorys[:int(self.memory_limit*self.memory_zip_rate)]
                mem_sum = self.zip_memory("\n".join([str(i) for i in willzip_memory]))
                self.memorys = [mem_sum] + self.memorys[int(self.memory_limit*self.memory_zip_rate)-1:]

    def add(self,content:List[perceive_unit]):
        self.memorys += content
        if self.zip_memory != None:
            if len(self.memorys) > self.memory_limit:
                willzip_memory = self.memorys[:int(self.memory_limit*self.memory_zip_rate)]
                mem_sum = self.zip_memory("\n".join([str(i) for i in willzip_memory]))
                self.memorys = [mem_sum] + self.memorys[int(self.memory_limit*self.memory_zip_rate)-1:]

    def get_time_memorys(self, start_time:datetime, end_time:datetime):
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time).astimezone(timezone.utc)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time).astimezone(timezone.utc)
        return self.storage_driver.find_by_time(start_time, end_time)
