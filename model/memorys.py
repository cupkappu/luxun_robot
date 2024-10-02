from .base_models import have_dict
from typing import Union, List
from dict2xml import dict2xml
from .doc import docs
from .adapter import db_drivers
import uuid as uuidl

class perceive_unit(have_dict):

    content: Union[str,dict]
    uuid: str

    def __init__(self, content:Union[str,dict],uuid: str = str(uuidl.uuid4()),**kwargs):
        self.content = content
        self.metadata = kwargs.get('metadata',{})
        self.uuid = uuid

    def __str__(self) -> str:
        if isinstance(self.content, str):
            return str(self.content)
        elif isinstance(self.content, dict):
            return dict2xml(self.content)
        return ""
    
    def to_dict(self) -> dict:
        return {
            'content': self.content
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
        metadata['type'] = 'perceive'
        if storage == 'memory':
            self.perceives = perceives
        else:
            metadata['type'] = 'perceive'
            self.storage_driver = db_drivers[storage](
                db_uri=db_uri,
                db_name=db_name,
                table=table,
                constructor=perceive_unit, 
                metadata = metadata)
            self.perceives = self.storage_driver.list_nums(nums=self.perceive_limit)
            
    def __str__(self) -> str:
        self.store_memory(self.perceives)
        result = "\n".join([str(i) for i in self.perceives])
        self.perceives = []
        return result

    def append(self, content: Union[str, dict]):
        new_perceive = perceive_unit(content=content)
        self.perceives.append(new_perceive)
        self.storage_driver.save_one(new_perceive)
        if self.store_memory is not None:
            if len(self.perceives) > self.perceive_limit:
                chunks = [self.perceives[i:i + self.perceive_limit] for i in range(0, len(self.perceives) - self.perceive_limit, self.perceive_limit)]
                for chunk in chunks:
                    try:
                        for perceive in chunk:
                            self.store_memory(perceive)
                    except Exception as e:
                        print(f"存儲記憶時出錯: {e}")
                self.perceives = self.perceives[-self.perceive_limit:]

class memory_list():

    memorys: List[perceive_unit]
    memory_limit: int = 30
    memory_zip_rate: float = 0.3
    zip_memory: callable

    def __init__(self, 
                 memorys: List[perceive_unit] = [], 
                 memory_limit:int = 30, 
                 zip_memory: callable = None, 
                 memory_zip_rate: float = 0.3,**kwargs
                 ):
        self.memorys = memorys
        self.memory_limit = memory_limit
        self.zip_memory = zip_memory
        self.memory_zip_rate = memory_zip_rate

    def __str__(self) -> str:
        return "\n".join([str(i) for i in self.memorys])
    
    def append(self,content:perceive_unit):
        self.memorys.append(content)
        if self.zip_memory != None:
            if len(self.memorys) > self.memory_limit:
                willzip_memory = self.memorys[:int(self.memory_limit*self.memory_zip_rate)]
                mem_sum = self.zip_memory("\n".join([str(i) for i in willzip_memory]))
                self.memorys = [mem_sum] + self.memorys[int(self.memory_limit*self.memory_zip_rate)-1:]

class memory_perceive_union:
    memorys: memory_list
    perceives: perceive_group
    def __init__(self, memorys: memory_list, perceives: perceive_group, doc_m:docs):
        self.memorys = memorys
        self.memorys.zip_memory = lambda x :doc_m.add_doc(x).get_summary()
        self.perceives = perceives
        self.perceives.store_memory = self.memorys.append
        self.docs = doc_m
    def get_unions(self):
        return self.memorys, self.perceives
