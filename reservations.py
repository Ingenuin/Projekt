from datetime import datetime as dt, timedelta
import streamlit as st
from desks import Desk
from users import User
from database_inheritance import DatabaseConnector
from streamlit_calendar import calendar

def reserve_desk(desks, plot_column):

    st.subheader("Reserve Desk")
    desk_name_to_reserve = st.selectbox("Select desk to reserve:", [desk['desk_name'] for desk in desks])
    user_email = st.selectbox("Select user for reservation:", [user['email'] for user in User.find_all()])

    # Date selection
    start_date = st.date_input("Select start date:", min_value=dt.today().date(), value=None)
    end_date = st.date_input("Select end date:")

    # Time selection
    start_time = st.time_input("Select start time:", key="start_time")
    end_time = st.time_input("Select end time:", key="end_time")

    calendar_visualisation(plot_column)   

    if st.button("Reserve Desk"):
        # Combine selected date with selected time to get start and end datetime
        start_datetime = dt.combine(start_date, start_time)
        end_datetime = dt.combine(end_date, end_time)
    
        handle_reserve_desk(desk_name_to_reserve, user_email, start_datetime, end_datetime)


def handle_reserve_desk(desk_name, user_email, start_datetime, end_datetime):
    desk_to_reserve = Desk.load_by_id(desk_name)
    if desk_to_reserve:
        if start_datetime < dt.now():
            st.error("Start datetime cannot be in the past.")
        elif end_datetime <= start_datetime:
            st.error("End datetime should be after start datetime.")
        else:
            DatabaseConnector().add_reservation_to_table(desk_name, user_email, start_datetime, end_datetime)
            st.success(f"Desk {desk_name} reserved successfully by {user_email} from {start_datetime} to {end_datetime}.")
    else:
        st.error("Desk not found.")

def change_reservation(desks, users):
    st.subheader("Change Reservation")

    user_email_to_change = st.selectbox("Select user for reservation change:", [user['email'] for user in users])

    desk_name_to_change = st.selectbox("Select desk for reservation change:", [desk['desk_name'] for desk in desks])

    current_reservations = DatabaseConnector().get_user_desk_reservations(user_email_to_change, desk_name_to_change)

    
    if not current_reservations:
        st.warning(f"No reservations found for user {user_email_to_change} and desk {desk_name_to_change}.")
        return

    st.subheader("Current Reservations")
    for reservation in current_reservations:
        start_datetime = dt.fromisoformat(reservation["start_datetime"])
        end_datetime = dt.fromisoformat(reservation["end_datetime"])
        st.write(f"Reservation from {start_datetime} to {end_datetime}")

    
    st.subheader("Select New Reservation Details")
    new_start_date = st.date_input("Select new start date:", min_value=dt.today().date(), value=None)
    new_end_date = st.date_input("Select new end date:")
    new_start_time = st.time_input("Select new start time:", key="new_start_time")
    new_end_time = st.time_input("Select new end time:", key="new_end_time")

    if st.button("Change Reservation"):
        
        new_start_datetime = dt.combine(new_start_date, new_start_time)
        new_end_datetime = dt.combine(new_end_date, new_end_time)

        
        if new_start_datetime < dt.now():
            st.error("New start datetime cannot be in the past.")
        elif new_end_datetime <= new_start_datetime:
            st.error("New end datetime should be after new start datetime.")
        else:
            
            DatabaseConnector().update_reservation(user_email_to_change, desk_name_to_change, new_start_datetime, new_end_datetime)
            st.success(f"Reservation for user {user_email_to_change} and desk {desk_name_to_change} changed successfully.")

def delete_reservation(desks, users):
    st.subheader("Delete Reservation")

    
    user_email_to_delete = st.selectbox("Select user for reservation deletion:", [user['email'] for user in users])
    desk_name_to_delete = st.selectbox("Select desk for reservation deletion:", [desk['desk_name'] for desk in desks])   
    current_reservations = DatabaseConnector().get_user_desk_reservations(user_email_to_delete, desk_name_to_delete)
    

    if not current_reservations:
        st.warning(f"No reservations found for user {user_email_to_delete} and desk {desk_name_to_delete}.")
        return

    st.subheader("Current Reservations")
    for reservation in current_reservations:
        start_datetime = dt.fromisoformat(reservation["start_datetime"])
        end_datetime = dt.fromisoformat(reservation["end_datetime"])
        st.write(f"Reservation from {start_datetime} to {end_datetime}")

    if st.button("Delete Reservation"):
        DatabaseConnector().delete_reservation(user_email_to_delete, desk_name_to_delete)
        st.success(f"Reservation for user {user_email_to_delete} and desk {desk_name_to_delete} deleted successfully.")


def calendar_visualisation(plot_column):
    reservations = DatabaseConnector().get_desk_reservations()

    calendar_events = []
    for reservation in reservations:
        start_datetime = dt.fromisoformat(reservation["start_datetime"])
        end_datetime = dt.fromisoformat(reservation["end_datetime"])
        calendar_events.append({
            "title": f"Desk {reservation['desk_name']} reserved by {reservation['user_email']}",
            "start": start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
        })

    # Define calendar options
    calendar_options = {
        "editable": False,
        "selectable": False,
        "initialView": "timeGridWeek",  # Display weekly view
        "slotMinTime": "06:00:00",
        "slotMaxTime": "20:00:00",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "timeGridWeek,timeGridDay",
        },
    }

    # Define custom CSS for calendar styling
    custom_css = """
        .fc-event-title {
            font-weight: bold;
        }
    """

    with plot_column:
        st.subheader("Appointment Overview")
        # Display the calendar
        selected_date = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)
        st.write(selected_date)