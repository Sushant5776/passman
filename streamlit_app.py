import streamlit as st
import sqlite3
from hashlib import sha256
import pandas as pd
import threading
import contextlib2

# Thread-local storage for database connections
_local_db = threading.local()

def get_db_connection():
    if not hasattr(_local_db, 'conn'):
        _local_db.conn = sqlite3.connect('passwords.db')
    return _local_db.conn

def close_db_connection():
    if hasattr(_local_db, 'conn'):
        _local_db.conn.close()
        del _local_db.conn

@contextlib2.contextmanager
def use_db():
    conn = get_db_connection()
    yield conn
    close_db_connection()

# Streamlit App
st.title("SafeEntry")
st.text('A secure way to manage your credentials')

# Cache the database query results
@st.cache_data
def get_all_passwords():
    with use_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM passwords")
        rows = c.fetchall()
        df = pd.DataFrame(rows, columns=["ID", "Username", "Password", "Website"])
        return df

# Add Password
new_website = st.text_input("Website")
new_username = st.text_input("Username")
new_password = st.text_input("Password", type="password")

if st.button("Save", use_container_width=True):
    hashed_password = sha256(new_password.encode()).hexdigest()  # Hash the password
    with use_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO passwords (username, password, website) VALUES (?, ?, ?)",
                    (new_username, hashed_password, new_website))
        conn.commit()
    st.success("Password added successfully!")
    st.cache_data.clear()

# View Passwords
st.header("View Passwords")
passwords_df = get_all_passwords()
st.table(passwords_df)

# Edit Password
if st.checkbox("Edit Password"):
    password_id = st.number_input("Enter ID of password to edit")
    if st.button("Find Password"):
        with use_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM passwords WHERE id=?", (password_id,))
            row = c.fetchone()
        if row:
            st.text_input("Website", value=row[3])
            st.text_input("Username", value=row[1])
            # Display hashed password (for security)
            st.text_input("Hashed Password", value=row[2])
            new_website = st.text_input("New Website (optional)")
            new_username = st.text_input("New Username (optional)")
            new_password = st.text_input("New Password (optional)", type="password")

            if st.button("Update"):
                if new_password:
                    hashed_password = sha256(new_password.encode()).hexdigest()
                else:
                    hashed_password = row[2]  # Use existing hashed password
                with use_db() as conn:
                    c = conn.cursor()
                    if new_website:
                        c.execute("UPDATE passwords SET username=?, password=?, website=? WHERE id=?",
                                 (new_username or row[1], hashed_password, new_website or row[3], password_id))
                    else:
                        c.execute("UPDATE passwords SET username=?, password=? WHERE id=?",
                                 (new_username or row[1], hashed_password, password_id))
                    conn.commit()
                st.success("Password updated successfully!")
                st.cache_data.clear() 
        else:
            st.warning("Password not found.")

# Delete Password
if st.checkbox("Delete Password"):
    password_id = st.number_input("Enter ID of password to delete")
    if st.button("Delete"):
        with use_db() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM passwords WHERE id=?", (password_id,))
            conn.commit()
        st.success("Password deleted successfully!")
        st.cache_data.clear()