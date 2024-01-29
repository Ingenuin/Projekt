import os
from tinydb import TinyDB
from tinydb.table import Table
from tinydb.storages import JSONStorage
from datetime import datetime, date, time
from tinydb_serialization import Serializer, SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

class DatabaseConnector:
    """
    Usage: DatabaseConnector().get_devices_table()
    The information about the actual database file path and the serializer objects has been abstracted away into this class
    """
    # Turns the class into a naive singleton
    # --> not thread safe and doesn't handle inheritance particularly well
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')

        return cls.__instance
    
    def get_devices_table(self) -> Table:
        return TinyDB(self.__instance.path, storage=serializer).table('devices')
    
    def get_users_table(self) -> Table:
        return TinyDB(self.__instance.path, storage=serializer).table('users')

#%%

class DateSerializer(Serializer):
    # The class this serializer handles --> must be date instead of datetime.date
    OBJ_CLASS = date

    def encode(self, obj):
        return obj.isoformat()

    def decode(self, s):
        return date.fromisoformat(s)

class TimeSerializer(Serializer):
    # The class this serializer handles --> must be time instead of datetime.time
    OBJ_CLASS = time
    
    def encode(self, obj):
        return obj.isoformat()

    def decode(self, s):
        return time.fromisoformat(s)

serializer = SerializationMiddleware(JSONStorage)
serializer.register_serializer(DateTimeSerializer(), 'TinyDateTime')
serializer.register_serializer(DateSerializer(), 'TinyDate')
serializer.register_serializer(TimeSerializer(), 'TinyTime')