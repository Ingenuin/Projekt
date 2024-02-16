import os
from tinydb import TinyDB, Query
from tinydb.table import Table
from tinydb.storages import JSONStorage
from datetime import datetime, date, time
from tinydb_serialization import Serializer, SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

class DatabaseConnector:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')
            cls.__instance.db = TinyDB(cls.__instance.path, storage=serializer)

        return cls.__instance
    
    def get_desks_table(self) -> Table:
        table_name = 'desks'
        desks_table = self.__instance.db.table(table_name)

        if not desks_table.contains(Query().id.exists()):
            initial_desk_data = {'id': 1, 'desk_name': '1', 'desk_type': '3D-printer'}           
            desks_table.insert(initial_desk_data)
        return desks_table
    
    def get_users_table(self) -> Table:
        table_name = 'users'
        if not self.__instance.db.table(table_name).contains(Query().id.exists()):
            self.__instance.db.table(table_name).insert({'id': 1, 'user_name': 'userone', 'email': 'userone@mci.edu'}) 
        return self.__instance.db.table(table_name)
    
    def get_registrierung_table(self) -> Table:
        return TinyDB(self.__instance.path, storage=serializer).table('login')

class DateSerializer(Serializer):
    OBJ_CLASS = date

    def encode(self, obj):
        return obj.isoformat()

    def decode(self, s):
        return date.fromisoformat(s)

class TimeSerializer(Serializer):
    OBJ_CLASS = time
    
    def encode(self, obj):
        return obj.isoformat()

    def decode(self, s):
        return time.fromisoformat(s)

serializer = SerializationMiddleware(JSONStorage)
serializer.register_serializer(DateTimeSerializer(), 'TinyDateTime')
serializer.register_serializer(DateSerializer(), 'TinyDate')
serializer.register_serializer(TimeSerializer(), 'TinyTime')
