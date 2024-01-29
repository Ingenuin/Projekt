import os
from datetime import datetime

from users import User
from serializer import Serializable
from database_inheritance import DatabaseConnector
from tinydb import Query

class Device(Serializable):

    def __init__(self, device_name: str, managed_by_user_id: str, end_of_life: datetime = None, creation_date: datetime = None, last_update: datetime = None):
        super().__init__(device_name)
        self.device_name = device_name
        # The user id of the user that manages the device
        # We don't store the user object itself, but only the id (as a key)
        self.managed_by_user_id = managed_by_user_id

        self.is_active = True
        self.end_of_life = end_of_life if end_of_life else datetime.today().date()
        self.__creation_date = creation_date if creation_date else datetime.today().date()
        self.__last_update = last_update if last_update else datetime.today().date()
    
    @classmethod
    def get_db_connector(cls):
        return DatabaseConnector().get_devices_table()

    def store(self):
        print("Storing device...")
        self.__last_update = datetime.today().date() # we need to update the last update date before storing the object
        super().store()
    
    @classmethod
    def load_by_id(cls, id):
        print("Loading device...")
        data = super().load_by_id(id)
        if data:
            return cls(data['device_name'], data['managed_by_user_id'], data['end_of_life'], data['_Device__creation_date'], data['_Device__last_update'])
        else:
            return None
    
    def delete(self):
        super().delete()
        print("Device deleted.")

    def __str__(self) -> str:
        return F"Device: {self.device_name} ({self.managed_by_user_id}) - Active: {self.is_active} - Created: {self.__creation_date} - Last Update: {self.__last_update}"

    def __repr__(self) -> str:
        return self.__str__()