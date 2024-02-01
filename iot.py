import streamlit as st
from users import User
from devices  import Table
from database_inheritance import DatabaseConnector
from database_inheritance import DateSerializer
from database_inheritance import TimeSerializer
from streamlit_option_menu import option_menu

table_types = ['3D-printer', 'soldering_station (workbench)', 'AC', 'plain', 'workbench']


def main():

    selected = option_menu(None, ["Home", "User", "Tables", 'Settings'], 
    icons=['house', 'universal-access', "ui-checks-grid", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal")

    if selected == "User":
        manage_users()
    elif selected == "Tables":
        manage_tables()


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


def manage_tables():
    tables  = Table.find_all()
    st.header("Table Management")

    st.image('Labor.png')
    #table_to_configure = st.selectbox("Select table to display/configure:", [table['table_name'] for table in tables])

    #sollte nur fuer admin sichtbar sein   
    action = st.radio("Select action:", ["Add Table", "Change Table", "Reserve Table", "Delete Table"])


    if action == "Add Table":
        # Add new table
        #st.subheader("Add New Table")
        table_name = st.text_input("Table ID:")
        selected_table_type = st.selectbox("Select a Tabletype:", table_types)

        if st.button("Add Table"):
            if not table_name or not selected_table_type:
                st.error("Table ID and Table type are required.")
            elif Table.load_by_id(table_name):
                st.error("Table_ID already used")
            else:
                new_table = Table(table_name, selected_table_type)
                new_table.store()
                st.success("Table added successfully!")


    elif action == "Change Table":

        table_to_change = st.selectbox("Select table to change:", [table['table_name'] for table in tables])#waehlfeld um tischnummer zu waehlen 
        selected_table = Table.load_by_id(table_to_change) #tisch wird mit id als objekt geladen
        current_table_type = selected_table.table_type #tischart des gewaehlten tischs wird festgelegt
        new_type = st.selectbox("Select new table type", table_types, index=table_types.index(current_table_type), key='change_table_selectbox')#neue tischart kann gewaehlt werden, die alte ist als default eingestellt
 
        if table_to_change:
            if st.button("Change"):
                change_table(table_to_change, new_type)
        else:
            st.error("Table not found.")
        

    elif action == "Delete Table":
        # Delete existing table
        #st.subheader("Delete Device")
        table_name_to_delete = st.selectbox("Select table name to delete:", [table['table_name'] for table in tables])

        if st.button("Delete Table"):
            delete_table(table_name_to_delete)


    tables_to_show = st.selectbox("Select table to display:", [table['table_name'] for table in tables])

    selected_table = Table.load_by_id(tables_to_show)
    if selected_table:
        st.text("Table Info:")
        st.text(f"  ID: {selected_table.id}")
        st.text(f"  Table Name: {selected_table.table_name}")
        st.text(f"Tableetype: {selected_table.table_type}")
    else:
        st.text("Table not found.")

def change_table(table_name, new_type):
    table_to_change = Table.load_by_id(table_name)
    table_to_change.table_type = new_type
    table_to_change.store()
    st.success("Table changed successfully!")


def delete_table(table_name):
    table_to_delete = Table.load_by_id(table_name)
    if table_to_delete:
        table_to_delete.delete()
        st.success("Table deleted successfully!")
    else:
        st.error("Table not found.")

if __name__ == "__main__":
    main()


