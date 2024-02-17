from serializer import Serializable
from database_inheritance import DatabaseConnector
from tinydb import Query

class User(Serializable):
    
    def __init__(self, name, email, password=None) -> None:
        super().__init__(email)
        self.name = name
        self.email = email
        self.password = password

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
            return cls(data['name'], data['email'], data.get('password'))  # Get password if exists
        else:
            return None
        
    def delete(self):
        super().delete()
        print("User deleted.")

    def check_login_credentials(self):
        # Check if the provided login credentials match any user in the database
        user_query = Query().name == self.name
        user_query &= Query().password == self.password
        return self.get_db_connector().contains(user_query)

    def __str__(self):
        return F"User: {self.name} ({self.email})"

    def __repr__(self):
        return self.__str__()

# Create an alias for User class as Registrierung
Registrierung = User
