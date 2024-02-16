import streamlit as st
from users import User
from desks import Desk
from registrierung import Registrierung
from tinydb import Query
from database_inheritance import DatabaseConnector
from streamlit_option_menu import option_menu
import reservations as rs
import reservations as rs

desk_types = ['3D-printer', 'soldering_station (workbench)', 'AC', 'plain', 'workbench']

st.set_page_config(layout="wide")
menu_column, plot_column = st.columns([1.5, 1])

def got_to_state_registrierung():
    st.session_state["state"] = "registrierung"

def got_to_state_login():
    st.session_state["state"] = "login"

def got_to_state_eingeloggt():
    st.session_state["state"] = "eingeloggt"

def main():

    if "state" not in st.session_state:
        st.header("Studierendenwerkstatt")

        st.button("Registrierung",on_click=got_to_state_registrierung)

        st.button("Login", on_click=got_to_state_login)


    elif st.session_state["state"] == "registrierung":
        with st.form("Registrierung"):
            st.header("Registrierung")
            
            registrierung_username = st.text_input("Name")
            registrierung_email = st.text_input("email")
            registrierung_password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("speichern")
            
                
            if submitted:
                new_registrierung = Registrierung(registrierung_username, registrierung_email, registrierung_password)
                new_registrierung.store()
                st.success("Registrierung successful!")
                got_to_state_login()
 
    elif st.session_state["state"] == "login":
        with st.form("Login"):
            st.header("Login")
            login_name = st.text_input("Name")
            login_password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user_query = Query().name == login_name
                user_query &= Query().password == login_password

                user_data = Registrierung.get_db_connector().get(user_query)

                if user_data:
                    st.success("Login successful!")
                    got_to_state_eingeloggt()
                    # Set the login state or perform other actions here
                else:
                    st.error("Invalid username or password.")
                    


    elif st.session_state["state"] == "eingeloggt":
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
            elif selected == "Resrvations":
                manage_reservations()


def manage_users():

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


def manage_desks():
    desks  = Desk.find_all()


    action = option_menu(None, ["Add", "Change", "Delete", "Reserve"], 
    icons=['plus', 'arrow-repeat', "x"], 
    menu_icon="cast", default_index=0, orientation="horizontal")

    if action == "Add":

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
    
    elif action == "Reserve":
        rs.reserve_desk()


    elif action == "Change":

        desk_to_change = st.selectbox("Select desk to change:", [desk['desk_name'] for desk in desks])#waehlfeld um tischnummer zu waehlen 
        selected_desk = Desk.load_by_id(desk_to_change) #tisch wird mit id als objekt geladen
        current_desk_type = selected_desk.desk_type #tischart des gewaehlten tischs wird festgelegt
        new_type = st.selectbox("Select new desk type", desk_types, index=desk_types.index(current_desk_type), key='change_desk_selectbox')#neue tischart kann gewaehlt werden, die alte ist als default eingestellt
 
        if desk_to_change:
            if st.button("Change"):
                change_desk(desk_to_change, new_type)
        else:
            st.error("Desk not found.")
        

    elif action == "Delete":

        desk_name_to_delete = st.selectbox("Select desk name to delete:", [desk['desk_name'] for desk in desks])

        if st.button("Delete Desk"):
            delete_desk(desk_name_to_delete)


    desk_to_show = st.selectbox("Select desk to display:", [desk['desk_name'] for desk in desks])

    selected_desk = Desk.load_by_id(desk_to_show)
    if selected_desk:
        st.text("Desk Info:")
        st.text(f"  ID: {selected_desk.id}")
        st.text(f"  Desk Name: {selected_desk.desk_name}")
        st.text(f"Desktype: {selected_desk.desk_type}")
    else:
        st.text("Desk not found.")

def change_desk(desk_name, new_type):
    desk_to_change = Desk.load_by_id(desk_name)
    desk_to_change.desk_type = new_type
    desk_to_change.store()
    st.success("Desk changed successfully!")


def delete_desk(desk_name):
    desk_to_delete = Desk.load_by_id(desk_name)
    if desk_to_delete:
        desk_to_delete.delete()
        st.success("Desk deleted successfully!")
    else:
        st.error("Desk not found.")


#def manage_reservations():


if __name__ == "__main__":
    main()