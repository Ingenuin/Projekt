from datetime import datetime as dt
from serializer import Serializable
from database_inheritance import DatabaseConnector
from tinydb import Query
from desks import Desk
from streamlit_option_menu import option_menu
from users import User
import streamlit as st


def reserve_desk():
    desks = Desk.find_all()
    st.subheader("Reserve Desk")
    desk_name_to_reserve = st.selectbox("Select desk to reserve:", [desk['desk_name'] for desk in desks])
    user_email = st.selectbox("Select user for reservation:", [user['email'] for user in User.find_all()])
    start_date = st.date_input("Select start date:", min_value=dt.today().date())
    end_date = st.date_input("Select end date:")

    if st.button("Reserve Desk"):
        handle_reserve_device(desk_name_to_reserve, user_email, start_date, end_date)

def handle_reserve_device(desk_name, user_email, start_date, end_date):
    device_to_reserve = Desk.load_by_id(desk_name)
    if device_to_reserve:
        device_to_reserve.add_reservation(user_email, start_date, end_date)
        st.success(f"Desk {desk_name} reserved successfully by {user_email} from {start_date} to {end_date}.")
    else:
        st.error("Desk not found.")

