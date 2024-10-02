from .base_models import have_dict
from typing import Union, List
from dict2xml import dict2xml
from .doc import docs

class perceive_unit():
    content: Union[str,dict]
    def __init__(self, content:Union[str,dict]):
        self.content = content
    def __str__(self) -> str:
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, dict):
            return dict2xml(self.content)
        return None
    
class perceive_group():
    perceives: List[perceive_unit]
    perceive_limit: int
    store_memory: callable
    def __init__(self, perceives:List[perceive_unit] = [], perceive_limit: int = 20, store_memory:callable = None):
        self.perceives = perceives
        self.perceive_limit = perceive_limit
        self.store_memory = store_memory
    def __str__(self) -> str:
        return "\n".join([str(i) for i in self.perceives])
    def append(self, content:Union[str, dict], ):
        self.perceives.append(perceive_unit(content=content))
        if self.store_memory != None:
            result = [self.perceives[i:i + self.perceive_limit] for i in range(0, len(self.perceives), self.perceive_limit)] if len(self.perceives) > self.perceive_limit else [[self.perceives]]
            for i in result[:-1]:
                self.store_memory(i)
            self.perceives = result[-1]

class memory_list():
    memorys: List[have_dict]
    memory_limit: int = 30
    memory_zip_rate: float = 0.3
    zip_memory: callable
    def __init__(self, memorys: List[have_dict] = [], memory_limit:int = 30, zip_memory: callable = None, memory_zip_rate: float = 0.3):
        self.memorys = memorys
        self.memory_limit = memory_limit
        self.zip_memory = zip_memory
        self.memory_zip_rate = memory_zip_rate
    def __str__(self):
        return "\n".join([str(i) for i in self.memorys])
    def append(self,content):
        if not isinstance(content, have_dict):
            self.memorys.append(perceive_unit(content))
        else:
            self.memorys.append(content)
        if self.zip_memory != None:
            if len(self.memorys) > self.memory_limit:
                willzip_memory = self.memorys[int(30*self.memory_zip_rate)]
                mem_sum = self.zip_memory(willzip_memory)
                self.memorys = [mem_sum] + self.memorys[int(30*self.memory_zip_rate)-1:]

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
    
