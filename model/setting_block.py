from .base_models import have_dict
from typing import List
import uuid as uuidl
from .adapter import db_drivers
from prompts.qq import init_query
from langchain_core.language_models import BaseChatModel
from prompts.role_gen import gen_role, gen_prompt
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

class setting_bolck(have_dict):
    personal_setting: str
    title: str = ''
    name: str = ''
    storys: List[str] = []
    prompt: str
    def __init__(self,personal_setting:str, 
                 title:str, 
                 name:str, 
                 storys:List[str] = [], 
                 prompt:str = '',
                 uuid: str = str(uuidl.uuid4()), *args, **kwargs):
        self.personal_setting = personal_setting
        self.title = title
        self.name = name
        self.uuid = uuid
        self.storys = storys
        if prompt == '':
            self.prompt = self.personal_setting
        else: self.prompt = str(prompt)
    def __str__(self, storys: bool = False, list_mode: bool = False) -> str:
        if storys:
            return f"{self.name}({self.uuid}):{self.personal_setting}\n{self.storys}"
        elif list_mode:
            return f"{self.name}({self.uuid}):{self.personal_setting}"
        else:
            return self.prompt

    def to_dict(self) -> dict:
        return {
            'personal_setting': self.personal_setting,
            'uuid': self.uuid,
            'title': self.title,
            'name': self.name,
            'storys': self.storys,
            'prompt': self.prompt
        }

class setting_format(BaseModel):
    setting: str = Field(description="The role setting.")
    story: List[str] = Field(description="The story of the role setting.")
    name: str = Field(description="The name of the role setting.")
    desc: str = Field(description="The description of the role setting.")

class setting_group():
    settings: List[setting_bolck]
    default: setting_bolck = None
    llm: BaseChatModel
    def __init__(self, 
                 settings: List[setting_bolck] = [],
                 storage: str = 'memory',
                 db_uri: str = '',
                    db_name: str = '',
                    table: str = '',
                    metadata: dict = {}, default: str = '', **kwargs):
        self.settings = settings
        self.metadata = metadata
        self.llm = kwargs.get('llm',None)
        if storage != 'memory':
            self.storage_driver = db_drivers[storage](
                db_uri=db_uri,
                db_name=db_name,
                table=table + '_setting',
                constructor=setting_bolck,
                metadata=self.metadata
            )
        self.storage = storage
        def set_default():
            new = setting_bolck(init_query['personal_setting'],'default','default',prompt='')
            self.add(new)
            self.default = new
        if default == '':
            for i in self.list_all():
                if i.title == 'default':
                    self.default = i
                    break
            if self.default == None:
                set_default()
    
    def gen(self,desc:str):
        chain = (gen_role |  
            self.llm.bind(response_format={"type": "json_object"}) | 
            JsonOutputParser(pydantic_object=setting_format))
        gen_prompt_chain = (gen_prompt|
                      self.llm.bind(response_format={"type": "json_object"}) | 
                      JsonOutputParser())
        result = chain.invoke({'desc':desc})
        prompt = gen_prompt_chain.invoke({'role':str(result)})
        
        print(prompt)
        setting = setting_bolck(result['setting'],
                                desc,
                                result['name'],
                                result['storys'],
                                prompt=prompt['prompt'])
        self.add(setting)
        return setting.to_dict()

    def add(self, setting: setting_bolck):
        if self.storage == 'memory': self.settings.append(setting)
        else: self.storage_driver.save_one(setting)

    def find(self, uuid: str, meta_on=True) -> setting_bolck:
        if self.storage == 'memory':
            for i in self.settings:
                if str(i.uuid) == uuid:
                    return i
            return None
        return self.storage_driver.find_one(uuid, meta_on)

    def set_default(self, uuid: str):
        new = self.find(uuid)
        self.storage_driver.change_content(self.default,new.to_dict())
        self.default = new
        return "personal setting has been set to " + self.default.name

    def list_all(self) -> List[setting_bolck]:
        if self.storage == 'memory':
            return self.settings
        return self.storage_driver.list_all_obj()
    
    def get_str(self, storys: bool = False) -> str:
        return "\n".join([i.__str__(storys=storys) for i in self.settings])
    
    def delete(self, uuid: str):
        if self.storage == 'memory':
            for i in self.settings:
                if str(i.uuid) == uuid:
                    self.settings.remove(i)
                    return True
            return False
        return self.storage_driver.delete_one(uuid)