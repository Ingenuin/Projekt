import os
from datetime import datetime

from users import User
from serializer import Serializable
from database_inheritance import DatabaseConnector
from tinydb import Query

table_types = ['3D-printer', 'soldering_station', 'AC', 'plain']

class Table(Serializable):

    def __init__(self, table_name: str, table_type: str):
        super().__init__(table_name)
        self.table_name = table_name
        self.table_type = table_type

    @classmethod
    def get_db_connector(cls):
        return DatabaseConnector().get_devices_table()

    def store(self):
        print("Storing table...")
        super().store()
    
    @classmethod
    def load_by_id(cls, id):
        print("Loading table...")
        data = super().load_by_id(id)
        if data:
            return cls(data['table_name'], data['table_type'])
        else:
            return None
    
    def delete(self):
        super().delete()
        print("Table deleted.")

    def __str__(self) -> str:
        return f"Table: {self.table_name} ({self.table_type})\n"

    def __repr__(self) -> str:
        return self.__str__()