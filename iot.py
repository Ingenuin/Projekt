import streamlit as st
from users import User
from desks import Desk
from reservation import Reservation 
from users import Registrierung
from tinydb import Query
from streamlit_option_menu import option_menu
import reservations as rs



st.set_page_config(layout="wide")
menu_column, plot_column = st.columns([1.2, 1])

def go_to_state_login():
    st.session_state["state"] = "login"

def go_to_state_logged_in_as_admin():
    st.session_state["state"] = "logged_in_a"

def go_to_state_logged_in_as_user():
    st.session_state["state"] = "logged_in_u"

def main():

    if "state" not in st.session_state:
        st.header("Student Workshop")
        go_to_state_login()

    if st.session_state["state"] == "login":
        login_form()

    elif st.session_state["state"] == "logged_in_a":
        display_admin_interface()

    elif st.session_state["state"] == "logged_in_u":
        display_user_interface()


def login_form():
    with st.form("Login"):
        st.header("Login")
        login_name = st.text_input("Email", placeholder="admin@mci.edu")
        login_password = st.text_input("Password", type="password", placeholder="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # Query the database to check if the provided credentials are valid
            user_query = Query().name == login_name
            user_query &= Query().password == login_password
            user_data = Registrierung.get_db_connector().get(user_query)

            if user_data:
                st.session_state["login_name"] = login_name
                if user_data['role'] == 'admin':
                    st.success("Admin login successful!")
                    go_to_state_logged_in_as_admin()
                else:
                    st.success("Regular user login successful!")
                    go_to_state_logged_in_as_user()
            else:
                st.error("Invalid username or password.")

def display_admin_interface():
    admin_role=True
    with plot_column:
        content_column, button_column = st.columns([1, 0.2])

        with button_column:
            st.button('Logout',on_click=go_to_state_login)
        st.image('Labor.png')

    with menu_column:
        st.header("Students Workshop")
        selected = option_menu(None, ["User", "Desks", "Reservations"], 
        icons=['universal-access', "ui-checks-grid", "calendar"], 
        menu_icon="cast", default_index=0, orientation="horizontal")

        if selected == "User":
            manage_users()
        elif selected == "Desks":
            manage_desks()
        elif selected == "Reservations":
            user_name = st.session_state["login_name"]
            student_id = st.session_state.get("student_id", None)
            manage_reservations(admin_role, user_name, student_id)

def display_user_interface():
    with plot_column:
        content_column, button_column = st.columns([1, 0.2])

        with button_column:
            if st.button('Logout'):
                st.session_state["state"] = "login"
        st.image('Labor.png')

    with menu_column:
        st.header("Students Workshop")
        admin_role = False
        user_email = st.session_state["login_name"]
        student_id = st.session_state.get("student_id", None)
        manage_reservations(admin_role, user_email, student_id)

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
    user_roles = ["admin", "user"]
    user_role = st.selectbox("Role:", user_roles)
    user_password = st.text_input("Password:", type="password", placeholder="Default: 12345678")
    student_id = st.text_input("Student ID:")

    if st.button("Add User"):
        if not user_name or not user_email or not user_password or not user_role:
            st.error("Name, email, role, and password are required.")
        elif User.load_by_id(user_email):
            st.error("Email already in use. Please choose a different email.")
        else:
            new_user = User(user_name, user_email, user_role, user_password, student_id)
            new_user.store()
            st.success("User added successfully!")

def change_user():
    st.subheader("Change User")
    user_email_to_change = st.selectbox("Select user to change name:", [user['email'] for user in User.find_all()])
    new_name = st.text_input("Enter new name:")
    new_password = st.text_input("Enter new password:", type="password")
    new_student_id = st.text_input("Enter new student ID:")

    if st.button("Change User"):
        user_to_change = User.load_by_id(user_email_to_change)
        if user_to_change:
            if new_name:
                user_to_change.name = new_name
            if new_password:
                user_to_change.password = new_password
            if new_student_id:
                user_to_change.student_id = new_student_id
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
    selected_user=User.load_by_id(user_to_show)

    if selected_user:
        st.text("User Info:")
        st.text(f"Name: {selected_user.name}")
        st.text(f"Email: {selected_user.email}")
        st.text(f"Role: {selected_user.role}")
    else:
        st.text("User not found.")


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

desk_types = ['3D-printer', 'soldering_station (workbench)', 'AC', 'plain', 'workbench']

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
    desk_to_show = st.selectbox("Select desk to display info:", [desk['desk_name'] for desk in desks])
    selected_desk = Desk.load_by_id(desk_to_show)

    if selected_desk:
        st.text("Desk Info:")
        st.text(f"  ID: {selected_desk.id}")
        st.text(f"Desktype: {selected_desk.desk_type}")
    else:
        st.text("Desk not found.")

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def manage_reservations(admin_role, user_name, student_id):
    desks = Desk.find_all()
    users = User.find_all()

    action = option_menu(None, ["Add", "Change", "Delete"],
                         icons=['plus', 'arrow-repeat', "x"],
                         menu_icon="cast", default_index=0, orientation="horizontal")

    if action == "Add":
        rs.reserve_desk(desks, plot_column, student_id)
    elif action == "Change":
        rs.change_reservation(desks, users, user_name, student_id)
    elif action == "Delete":
        rs.delete_reservation(student_id)





if __name__ == "__main__":
    main()
