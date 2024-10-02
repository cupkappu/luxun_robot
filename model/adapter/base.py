from abc import ABC,abstractmethod
class Adapter(ABC):
    @abstractmethod
    def __init__(self, db_uri:str,db_name:str,table:str):
        pass
    @abstractmethod
    def save_one(self, content):
        pass
    @abstractmethod
    def find_one(self, content):
        pass
    @abstractmethod
    def delete_one(self, content):
        pass
    @abstractmethod
    def list_all(self):
        pass
    def list_nums(self):
        pass