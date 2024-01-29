from serializer import Serializable
from database_inheritance import DatabaseConnector
from tinydb import Query

class User(Serializable):
    
    def __init__(self, name, email) -> None:
        super().__init__(email)
        self.name = name
        self.email = email

    @classmethod
    def get_db_connector(cls):
        return DatabaseConnector().get_users_table()

    def store(self):
        print("Storing user...")
        super().store()

    @classmethod
    def load_by_id(cls, id):
        print("Loading user...")
        data = super().load_by_id(id)
        if data:
            return cls(data['name'], data['email'])
        else:
            return None
        
    def delete(self):
        super().delete()
        print("User deleted.")

    def __str__(self):
        return F"User: {self.name} ({self.email})"

    def __repr__(self):
        return self.__str__()

