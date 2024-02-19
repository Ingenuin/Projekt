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

        if not desks_table:
            # Initialize desks data with 14 desks
            initial_desk_data = [{'id': str(i), 'desk_name': str(i), 'desk_type': '3D-printer'} for i in range(1, 15)]
            desks_table.insert_multiple(initial_desk_data)

        return desks_table

    
    def get_users_table(self) -> Table:
        table_name = 'users'
        if not self.__instance.db.table(table_name).contains(Query().id.exists()):
            self.__instance.db.table(table_name).insert({'id': 'admin@mci.edu', 'name': 'Admin', 'email': 'admin@mci.edu', 'role':'admin', 'password': 'password'}) 
        return self.__instance.db.table(table_name)

    def add_reservation_to_table(self, desk_name, user_email, start_datetime, end_datetime):
        desks_table = self.get_desks_table()
        desk_query = Query().desk_name == desk_name
        desk_entry = desks_table.get(desk_query)

        if desk_entry:
            reservation_data = {
                'desk_name': desk_name,
                'user_email': user_email,
                'start_datetime': start_datetime.isoformat(),
                'end_datetime': end_datetime.isoformat()
            }
            desk_entry.setdefault('reservations', []).append(reservation_data)
            desks_table.update(desk_entry, desk_query)
            return True
        else:
            return False
        
    def get_desk_reservations(self) -> list:
        desks_table = self.get_desks_table()
        reservations = []
        for desk_entry in desks_table.all():
            if "reservations" in desk_entry:
                reservations.extend(desk_entry["reservations"])
        return reservations

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
