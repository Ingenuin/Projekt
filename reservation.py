from serializer import Serializable
from database_inheritance import DatabaseConnector
from tinydb import Query

class Reservation(Serializable):
    def __init__(self, id, desk_name, user_email, start_datetime, end_datetime, student_id):
        super().__init__(id)
        self.desk_name = desk_name
        self.user_email = user_email
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.student_id = student_id

    def store(self):
        print("HS")
        # Assuming 'reservation_id' is the unique identifier for each reservation

        super().store()
            #self.get_db_connector().update({'data': self.to_dict()}, Query().id == self.student_id)

            #self.get_db_connector().insert({'data': self.to_dict()})

    def delete(self):
        DatabaseConnector().delete_reservation(self.desk_name, self.student_id)

    @classmethod
    def get_db_connector(cls):
        return DatabaseConnector().get_reservations_table()
    
    @classmethod
    def load_by_id(cls, id):
        print("Loading desk...")
        data = super().load_by_id(id)
        if data:
            return cls(data['student_id'], data['email'])
        else:
            return None       

    @classmethod
    def load_all(cls):
        reservations = DatabaseConnector().get_all_reservations()
        return [cls(**reservation) for reservation in reservations]

    def __repr__(self):
        return f"Reservation(desk_name={self.desk_name}, user_email={self.user_email}, start_datetime={self.start_datetime}, end_datetime={self.end_datetime}, student_id={self.student_id})"

    def __str__(self):
        return f"Reservation: {self.desk_name} - {self.start_datetime} to {self.end_datetime} (Student ID: {self.student_id})"
