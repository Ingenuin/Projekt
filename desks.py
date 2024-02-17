from serializer import Serializable
from database_inheritance import DatabaseConnector
from tinydb import Query

desk_types = ['3D-printer', 'soldering_station', 'AC', 'plain']

class Desk(Serializable):

    def __init__(self, desk_name: str, desk_type: str):
        super().__init__(desk_name)
        self.desk_name = desk_name
        self.desk_type = desk_type

    @classmethod
    def get_db_connector(cls):
        return DatabaseConnector().get_desks_table()

    def store(self):
        print("Storing desk...")
        super().store()
    
    @classmethod
    def load_by_id(cls, id):
        print("Loading desk...")
        data = super().load_by_id(id)
        if data:
            return cls(data['desk_name'], data['desk_type'])
        else:
            return None
    
    def delete(self):
        super().delete()
        print("Desk deleted.")

    def __str__(self) -> str:
        return f"Desk: {self.desk_name} ({self.desk_type})\n"

    def __repr__(self) -> str:
        return self.__str__()