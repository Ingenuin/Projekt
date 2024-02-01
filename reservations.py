import datetime
from serializer import Serializable
from database_inheritance import DatabaseConnector
from tinydb import Query
from devices import Desk
import streamlit as st 
from streamlit_option_menu import option_menu
from users import User


def reserve_desk():
    desk = Desk.find_all()
    st.subheader("Reserve Device")
    device_name_to_reserve = st.selectbox("Select device to reserve:", [desk['desk_name'] for desk in desks])
    user_email = st.selectbox("Select user for reservation:", [user['email'] for user in User.find_all()])
    start_date = st.date_input("Select start date:", min_value=datetime.today().date())
    end_date = st.date_input("Select end date:")

    if st.button("Reserve Device"):
        handle_reserve_device(device_name_to_reserve, user_email, start_date, end_date)

def handle_reserve_device(device_name, user_email, start_date, end_date):
    device_to_reserve = Desk.load_by_id(device_name)
    if device_to_reserve:
        device_to_reserve.add_reservation(user_email, start_date, end_date)
        st.success(f"Device {desk_name} reserved successfully by {user_email} from {start_date} to {end_date}.")
    else:
        st.error("Device not found.")

