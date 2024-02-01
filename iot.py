import streamlit as st
from users import User
from devices import Device
from tinydb import Query
from registrierung import Registrierung
from database_inheritance import DatabaseConnector
from database_inheritance import DateSerializer
from database_inheritance import TimeSerializer
from streamlit_option_menu import option_menu

class Login:
    def __init__(self):
        self.username = None
        self.password = None
        self.role = None
        self.logged_in = False

def get_session_state():
    if "login" not in st.session_state:
        st.session_state.login = Login()
    if "registrierung" not in st.session_state:
        st.session_state.registrierung = Registrierung()
    return st.session_state.login, st.session_state.registrierung


def login():
    st.sidebar.header("Login")
    login_instance = get_session_state()

    # Check the login status
    if not login_instance.logged_in:
        # Get username and password from user input
        login_instance.username = st.sidebar.text_input("Name")
        login_instance.password = st.sidebar.text_input("Password", type="password")

        # Check if username and password are valid
        if st.sidebar.button("Login"):
            if validate_credentials(login_instance.username, login_instance.password):
                login_instance.logged_in = True
                login_instance.role = determine_role(login_instance.username)
                st.sidebar.success("Login successful!")

    return login_instance.logged_in

def registrierung():
    with st.form("Registrierung"):
        st.header("Registrierung")
        
        registrierung_username = st.text_input("Name")
        registrierung_email = st.text_input("email")
        registrierung_password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("speichern")
            # Check if username and password are valid
        if submitted:
            new_registrierung = Registrierung(registrierung_username, registrierung_email, registrierung_password)
            new_registrierung.store()
            st.success("Registrierung successful!")
       

    

def validate_credentials(username, password):
    allowed_users = {"admin": "password1", "student": "password2"} 
    return username in allowed_users and password == allowed_users[username]

def determine_role(username):
    # Determine the role of the user based on their username
    if username == "admin":
        return "admin"
    elif username == "student":
        return "student"
    else:
        return None
    
def got_to_state_registrierung():
    st.session_state["state"] = "registrierung"

def got_to_state_login():
    st.session_state["state"] = "login"

def got_to_state_eingeloggt():
    st.session_state["state"] = "eingeloggt"

def main():
    st.header("Studierendenwerkstatt")
    if "state" not in st.session_state:

        if st.button("Registrierung"):
            got_to_state_registrierung()

        elif st.button("Login"):
            got_to_state_login()


    elif st.session_state["state"] == "registrierung":
        with st.form("Registrierung"):
            st.header("Registrierung")
            
            registrierung_username = st.text_input("Name")
            registrierung_email = st.text_input("email")
            registrierung_password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("speichern")
            got_to_state_login()
                
            if submitted:
                new_registrierung = Registrierung(registrierung_username, registrierung_email, registrierung_password)
                new_registrierung.store()
                st.success("Registrierung successful!")

 
    elif st.session_state["state"] == "login":
        with st.form("Login"):
            st.header("Login")
            login_name = st.text_input("Name")
            login_password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                # Check login credentials against the database
                user_query = Query().email == login_name
                user_query &= Query().password == login_password

                user_data = Registrierung.get_db_connector().get(user_query)

                if user_data:
                    st.success("Login successful!")
                    # Set the login state or perform other actions here
                else:
                    st.error("Invalid username or password.")
            
        
 
def manage_users():
    st.header("User Management")

    action = option_menu(None, ["Add", "Change", "Delete"], 
    icons=['plus', 'arrow-repeat', "x"], 
    menu_icon="cast", default_index=0, orientation="horizontal")

     # Add new user
    if action == "Add":
        st.subheader("Add New User")
        user_name = st.text_input("Name:")
        user_email = st.text_input("Email:")

        if st.button("Add User"):
            if not user_name or not user_email:
                st.error("Both name and email are required.")
            elif User.load_by_id(user_email):
                st.error("Email already in use. Please choose a different email.")
            else:
                new_user = User(user_name, user_email)
                new_user.store()
                st.success("User added successfully!")
                
    if action == "Change":
        # Change existing user (only allows changing the name)
        st.subheader("Change User")

        # Create a selectbox with the list of user emails
        user_email_to_change = st.selectbox("Select user to change name:", [user['email'] for user in User.find_all()])

        new_name = st.text_input("Enter new name:")

        if st.button("Change User"):
            change_user(user_email_to_change, new_name)
            

    elif action == "Delete":
        # Delete existing user
        st.subheader("Delete User")
        user_email_to_delete = st.selectbox("Select user to delete:", [user['email'] for user in User.find_all()])

        if st.button("Delete User"):
            delete_user(user_email_to_delete)

        # Display existing users
    st.subheader("Existing Users")

    user_to_show = st.selectbox("Select user to display:", [user['email'] for user in User.find_all()])
    st.text(User.load_by_id(user_to_show))



def change_user(user_email, new_name):
    user_to_change = User.load_by_id(user_email)
    if user_to_change:
        user_to_change.name = new_name
        user_to_change.store()
        st.success("User changed successfully!")
    else:
        st.error("User not found.")   
    
def delete_user(user_email):
    user_to_delete = User.load_by_id(user_email)
    if user_to_delete:
        user_to_delete.delete()
        st.success("User deleted successfully!")
    else:
        st.error("User not found.")


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def manage_devices():
    st.header("Device Management")

    # Choose device action (add, change, or delete)
    action = st.radio("Select action:", ["Add Device", "Change Device", "Delete Device"])
   
    if action == "Add Device":
        # Add new device
        st.subheader("Add New Device")
        device_name = st.text_input("Device Name:")
        managed_by_user_id = st.selectbox("Select responsible user:", [user['email'] for user in User.find_all()])


        if st.button("Add Device"):
            if not device_name or not managed_by_user_id:
                st.error("Device name, device ID, and responsible user ID are required.")
            elif not User.load_by_id(managed_by_user_id):
                st.error("Invalid responsible user ID. Please provide a valid user ID.")
            else:
                new_device = Device(device_name, managed_by_user_id)
                new_device.store()
                st.success("Device added successfully!")
    elif action == "Change Device":
        # Change existing device (only allows changing the name)
        st.subheader("Change Device")
        device_name_to_change = st.text_input("Enter device name to change:")
        new_name = st.text_input("Enter new name:")

        if st.button("Change Device"):
            change_device(device_name_to_change, new_name)

    elif action == "Delete Device":
        # Delete existing device
        st.subheader("Delete Device")
        device_name_to_delete = st.text_input("Enter device name to delete:")

        if st.button("Delete Device"):
            delete_device(device_name_to_delete)

    devices = Device.find_all()
    devices_to_show = st.selectbox("Select device to display:", [device['device_name'] for device in devices])

    selected_device = Device.load_by_id(devices_to_show)
    if selected_device:
        st.text("Device Info:")
        st.text(f"  ID: {selected_device.id}")
        st.text(f"  Device Name: {selected_device.device_name}")
        st.text(f"  Managed By User ID: {selected_device.managed_by_user_id}")
        st.text(f"  Is Active: {selected_device.is_active}")
        st.text(f"  End of Life: {selected_device.end_of_life}")
        st.text(f"  Creation Date: {selected_device._Device__creation_date}")
        st.text(f"  Last Update: {selected_device._Device__last_update}")
    else:
        st.text("Device not found.")

def change_device(device_name, new_name):
    device_to_change = Device.load_by_id(device_name)
    if device_to_change:
        device_to_change.name = new_name
        device_to_change.store()
        st.success("Device changed successfully!")
    else:
        st.error("Device not found.")

def delete_device(device_name):
    device_to_delete = Device.load_by_id(device_name)
    if device_to_delete:
        device_to_delete.delete()
        st.success("Device deleted successfully!")
    else:
        st.error("Device not found.")

if __name__ == "__main__":
    main()