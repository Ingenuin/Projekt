import streamlit as st
from users import User
from devices import Device
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
    # Use SessionState to track the login status
    if "login" not in st.session_state:
        st.session_state.login = Login()
    return st.session_state.login

def login():
    st.sidebar.header("Login")
    login_instance = get_session_state()

    # Check the login status
    if not login_instance.logged_in:
        # Get username and password from user input
        login_instance.username = st.sidebar.text_input("Username")
        login_instance.password = st.sidebar.text_input("Password", type="password")

        # Check if username and password are valid
        if st.sidebar.button("Login"):
            if validate_credentials(login_instance.username, login_instance.password):
                login_instance.logged_in = True
                login_instance.role = determine_role(login_instance.username)
                st.sidebar.success("Login successful!")

    return login_instance.logged_in

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

def main():
    login_instance = get_session_state()

    if not login_instance.logged_in:
        # Show login fields only if not logged in
        login()

    if login_instance.logged_in:

        # Check user role before displaying certain options
        if login_instance.role == "admin":
            selected = option_menu(None, ["Home", "User", "Devices", 'Settings'],
                               icons=['house', 'universal-access', "tools", 'gear'],
                               menu_icon="cast", default_index=0, orientation="horizontal")
            
            if selected == "User":
                manage_users()
            elif selected == "Devices":
                manage_devices()

        elif login_instance.role == "student":
            selected = option_menu(None, ["Home", "User"],
                               icons=['house', 'universal-access', "tools", 'gear'],
                               menu_icon="cast", default_index=0, orientation="horizontal")
            if selected == "User":
                manage_users()
            

    # Additional UI elements to hide the login fields after successful login
    if login_instance.logged_in:
        st.sidebar.text(f"Logged in as {login_instance.role}: {login_instance.username}")
        st.sidebar.button("Logout", on_click=logout)

def logout():
    st.sidebar.success("Logged out successfully!")
    st.session_state.login.logged_in = False
    st.session_state.login.role = None

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