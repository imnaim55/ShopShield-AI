"""
Admin Authentication Module - ShopShield AI
Developed by Naim Shaikh
"""

import streamlit as st
import hashlib
import os
import json
from datetime import datetime

# Constants
ADMIN_FILE = "data/admin_credentials.json"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "ShopShield2024!"


def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_admin_file():
    """Create admin credentials file if it doesn't exist."""
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists(ADMIN_FILE):
        credentials = {
            "admin": {
                "password": hash_password(DEFAULT_PASSWORD),
                "created": datetime.now().isoformat(),
                "last_login": None
            }
        }
        with open(ADMIN_FILE, 'w') as f:
            json.dump(credentials, f, indent=4)
        
        print(f"Admin credentials created at {ADMIN_FILE}")
        print(f"Username: {DEFAULT_USERNAME}")
        print(f"Password: {DEFAULT_PASSWORD}")
        print("IMPORTANT: Change the default password immediately!")


def verify_login(username, password):
    """Verify admin login credentials."""
    if not os.path.exists(ADMIN_FILE):
        create_admin_file()
    
    try:
        with open(ADMIN_FILE, 'r') as f:
            credentials = json.load(f)
        
        if username in credentials:
            hashed = hash_password(password)
            if credentials[username]["password"] == hashed:
                # Update last login timestamp
                credentials[username]["last_login"] = datetime.now().isoformat()
                with open(ADMIN_FILE, 'w') as f:
                    json.dump(credentials, f, indent=4)
                return True
    except:
        pass
    
    return False


def change_password(username, old_password, new_password):
    """Change admin password."""
    if not verify_login(username, old_password):
        return False
    
    try:
        with open(ADMIN_FILE, 'r') as f:
            credentials = json.load(f)
        
        credentials[username]["password"] = hash_password(new_password)
        
        with open(ADMIN_FILE, 'w') as f:
            json.dump(credentials, f, indent=4)
        return True
    except:
        return False


def login_required(func):
    """Decorator to require login for admin pages."""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('admin_logged_in', False):
            st.error("Admin access required")
            st.info("Please login to access the admin dashboard")
            return None
        return func(*args, **kwargs)
    return wrapper


def login_page():
    """Display admin login page."""
    st.title("Admin Login")
    st.write("Enter your credentials to access the admin dashboard.")
    
    # Change password option
    if st.checkbox("Change Password"):
        st.subheader("Change Password")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            username = st.text_input("Username", value="admin", key="change_user")
        with col2:
            old_password = st.text_input("Current Password", type="password", key="old_pass")
        with col3:
            new_password = st.text_input("New Password", type="password", key="new_pass")
        
        if st.button("Update Password"):
            if change_password(username, old_password, new_password):
                st.success("Password changed successfully")
            else:
                st.error("Failed to change password. Please check your current password.")
        
        st.divider()
        st.subheader("Login")
    
    # Login form
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", key="login_user")
    with col2:
        password = st.text_input("Password", type="password", key="login_pass")
    
    if st.button("Login", use_container_width=True):
        if verify_login(username, password):
            st.session_state.admin_logged_in = True
            st.session_state.admin_username = username
            st.success(f"Welcome {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")


def logout():
    """Logout admin user."""
    st.session_state.admin_logged_in = False
    st.session_state.admin_username = None
    st.success("Logged out successfully")
    st.rerun()


# Initialize admin credentials on first run
if __name__ == "__main__":
    create_admin_file()