import streamlit as st
from users import User
from desks import Desk
from users import Registrierung
from tinydb import Query
from database_inheritance import DatabaseConnector
from streamlit_option_menu import option_menu
import reservations as rs


desk_types = ['3D-printer', 'soldering_station (workbench)', 'AC', 'plain', 'workbench']

st.set_page_config(layout="wide")
menu_column, plot_column = st.columns([1.5, 1])

def go_to_state_login():
    st.session_state["state"] = "login"

def go_to_state_logged_in_as_admin():
    st.session_state["state"] = "logged_in_A"

def go_to_state_logged_in_as_user():
    st.session_state["state"] = "logged_in_U"

def main():

    if "state" not in st.session_state:
        st.header("Studierendenwerkstatt")
        go_to_state_login()

    if st.session_state["state"] == "login":
        login_form()

    elif st.session_state["state"] == "logged_in_A":
        display_dashboard()

def login_form():
    with st.form("Login"):
        st.header("Login")
        login_name = st.text_input("Name", placeholder="admin")
        login_password = st.text_input("Password", type="password",placeholder="12345678")
        submit = st.form_submit_button("Login")
        
        if submit:
            user_query = Query().name == login_name
            user_query &= Query().password == login_password

            user_data = Registrierung.get_db_connector().get(user_query)

            if user_data:
                st.success("Login successful!")
                go_to_state_logged_in_as_admin()
            else:
                st.error("Invalid username or password.")

def display_dashboard():
    with plot_column:
        st.image('Labor.png')

    with menu_column:
        st.header("Studierendenwerkstatt")
        selected = option_menu(None, ["User", "Desks", "Reservations"], 
        icons=['universal-access', "ui-checks-grid", "calendar"], 
        menu_icon="cast", default_index=0, orientation="horizontal")

        if selected == "User":
            manage_users()
        elif selected == "Desks":
            manage_desks()
        elif selected == "Reservations":
            manage_reservations()

def manage_users():
    action = option_menu(None, ["Add", "Change", "Delete"], 
    icons=['plus', 'arrow-repeat', "x"], 
    menu_icon="cast", default_index=0, orientation="horizontal")

    if action == "Add":
        add_new_user()

    elif action == "Change":
        change_user()

    elif action == "Delete":
        delete_user()

    display_existing_users()

def add_new_user():
    st.subheader("Add New User")
    user_name = st.text_input("Name:")
    user_email = st.text_input("Email:")
    user_password = st.text_input("Password:", type="password", placeholder="Default: 12345678")

    if st.button("Add User"):
        if not user_name or not user_email or not user_password:
            st.error("Name, email, and password are required.")
        elif User.load_by_id(user_email):
            st.error("Email already in use. Please choose a different email.")
        else:
            new_user = User(user_name, user_email, user_password)
            new_user.store()
            st.success("User added successfully!")

def change_user():
    st.subheader("Change User")
    user_email_to_change = st.selectbox("Select user to change name:", [user['email'] for user in User.find_all()])
    new_name = st.text_input("Enter new name:")
    new_password = st.text_input("Enter new password:", type="password")

    if st.button("Change User"):
        user_to_change = User.load_by_id(user_email_to_change)
        if user_to_change:
            if new_name:
                user_to_change.name = new_name
            if new_password:
                user_to_change.password = new_password
            user_to_change.store()
            st.success("User changed successfully!")
        else:
            st.error("User not found.")


def delete_user():
    st.subheader("Delete User")
    user_email_to_delete = st.selectbox("Select user to delete:", [user['email'] for user in User.find_all()])

    if st.button("Delete User"):
        user_to_delete = User.load_by_id(user_email_to_delete)
        if user_to_delete:
            user_to_delete.delete()
            st.success("User deleted successfully!")
        else:
            st.error("User not found.")

def display_existing_users():
    st.subheader("Existing Users")
    user_to_show = st.selectbox("Select user to display:", [user['email'] for user in User.find_all()])
    st.text(User.load_by_id(user_to_show))


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def manage_desks():
    desks = Desk.find_all()

    action = option_menu(None, ["Add", "Change", "Delete"], 
                         icons=['plus', 'arrow-repeat', "x"], 
                         menu_icon="cast", default_index=0, orientation="horizontal")

    if action == "Add":
        add_desk()

    elif action == "Change":
        change_desk_type(desks)

    elif action == "Delete":
        delete_desk(desks)

    display_desk_info(desks)

def add_desk():
    desk_name = st.text_input("Desk ID:")
    selected_desk_type = st.selectbox("Select a Desktype:", desk_types)

    if st.button("Add Desk"):
        if not desk_name or not selected_desk_type:
            st.error("Desk ID and Desk type are required.")
        elif Desk.load_by_id(desk_name):
            st.error("Desk already used")
        else:
            new_desk = Desk(desk_name, selected_desk_type)
            new_desk.store()
            st.success("Desk added successfully!")

def change_desk_type(desks):
    desk_to_change = st.selectbox("Select desk to change:", [desk['desk_name'] for desk in desks])
    selected_desk = Desk.load_by_id(desk_to_change)

    if desk_to_change:
        current_desk_type = selected_desk.desk_type
        new_type = st.selectbox("Select new desk type", desk_types, index=desk_types.index(current_desk_type), key='change_desk_selectbox')

        if st.button("Change"):
            selected_desk.desk_type = new_type
            selected_desk.store()
            st.success("Desk changed successfully!")
    else:
        st.error("Desk not found.")

def delete_desk(desks):
    desk_name_to_delete = st.selectbox("Select desk name to delete:", [desk['desk_name'] for desk in desks])

    if st.button("Delete Desk"):
        desk_to_delete = Desk.load_by_id(desk_name_to_delete)

        if desk_to_delete:
            desk_to_delete.delete()
            st.success("Desk deleted successfully!")
        else:
            st.error("Desk not found.")

def display_desk_info(desks):
    desk_to_show = st.selectbox("Select desk to display:", [desk['desk_name'] for desk in desks])
    selected_desk = Desk.load_by_id(desk_to_show)

    if selected_desk:
        st.text("Desk Info:")
        st.text(f"  ID: {selected_desk.id}")
        st.text(f"  Desk Name: {selected_desk.desk_name}")
        st.text(f"Desktype: {selected_desk.desk_type}")
    else:
        st.text("Desk not found.")

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def manage_reservations():
    desks = Desk.find_all()
    action = option_menu(None, ["Add", "Change", "Delete"], 
                        icons=['plus', 'arrow-repeat', "x"], 
                        menu_icon="cast", default_index=0, orientation="horizontal")
    
    if action == "Add":
        rs.reserve_desk(desks, plot_column)

        
if __name__ == "__main__":
    main()
