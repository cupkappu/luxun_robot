from pymongo import MongoClient
from .base import Adapter
from ..base_models import *

class MongoAdapter(Adapter):
    def __init__(self, db_uri:str,db_name:str,table:str, constructor:callable, metadata:dict = {}):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.table = self.db[table]
        self.source_class_constructor = constructor
        self.metadata = metadata
    def save_one(self, content:have_dict):
        data = content.to_dict()
        data.update({'metadata':self.metadata})
        self.table.insert_one(data)
    def find_one(self, uuid:str, meta_on: bool):
        if meta_on:
            doc_dict = self.table.find_one({"uuid": uuid, 'metadata':self.metadata})
        else:
            doc_dict = self.table.find_one({"uuid": uuid,})
        if doc_dict:
            return self.source_class_constructor(**doc_dict)
        return None
    def delete_one(self, uuid:str):
        result = self.table.delete_one({"uuid": uuid,'metadata':self.metadata})
        return result.deleted_count > 0