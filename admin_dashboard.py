"""
Admin Dashboard - ShopShield AI
Developed by Naim Shaikh
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import pytz
from auto_train import auto_retrain
from feedback_storage import get_feedback, get_feedback_count, get_archive_feedback
from url_analyzer import get_model_info

st.set_page_config(
    page_title="Admin Dashboard - ShopShield AI",
    page_icon="",
    layout="wide"
)

# Session State
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'retrain_success_time' not in st.session_state:
    st.session_state.retrain_success_time = None


def get_indian_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)


def login_page():
    # Use columns to center the entire login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Centered login container using HTML
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="font-size: 2.5rem; margin-bottom: 0; font-weight: 600;">Admin Login</h1>
                <p style="font-size: 1.1rem; color: #666; margin-top: 10px; margin-bottom: 30px;">
                    Enter your credentials to access the admin dashboard.
                </p>
                <hr style="margin: 20px 0; border: 0; border-top: 1px solid #e0e0e0;">
            </div>
        """, unsafe_allow_html=True)
        
        # Username field
        st.markdown('<div style="text-align: left;">', unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter username", key="admin_user")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Password field
        st.markdown('<div style="text-align: left;">', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder="Enter password", key="admin_pass")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Login button
        if st.button("Login", use_container_width=True, key="admin_login"):
            if username == "admin" and password == "ShopShield2024!":
                st.session_state.admin_logged_in = True
                st.session_state.admin_username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")


if not st.session_state.admin_logged_in:
    login_page()
    st.stop()

# Main Dashboard
st.title("Admin Dashboard")

# Sidebar
with st.sidebar:
    st.write(f"Logged in as: admin")
    if st.button("Logout", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.rerun()
    
    st.divider()
    
    if st.button("Force Retrain", use_container_width=True):
        with st.spinner("Retraining model..."):
            try:
                success = auto_retrain(min_samples=1, force=True)
                if success:
                    current_time = get_indian_time()
                    st.session_state.retrain_success_time = current_time.strftime("%d-%m-%Y %H:%M:%S IST")
                    st.success(f"Model retrained successfully at {st.session_state.retrain_success_time}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Retraining failed. Check logs.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Metrics
feedback_count = get_feedback_count()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Feedback", feedback_count)
with col2:
    st.metric("Ready for Retraining", "Yes" if feedback_count >= 5 else "No")
with col3:
    st.metric("Last Retrain", st.session_state.retrain_success_time or "Never")

if feedback_count >= 5:
    st.success(f"{feedback_count} feedback entries ready for retraining")
    st.progress(min(feedback_count / 10, 1.0))
else:
    st.info(f"{feedback_count}/5 feedback entries needed for retraining")
    st.progress(feedback_count / 5)

st.divider()

st.subheader("Current Feedback")
df_feedback = get_feedback()
if not df_feedback.empty:
    st.dataframe(df_feedback.tail(10), use_container_width=True)
    st.caption(f"Showing last 10 of {len(df_feedback)} entries")
else:
    st.info("No feedback collected yet")

st.divider()

st.subheader("Archived Feedback")
df_archive = get_archive_feedback()
if not df_archive.empty:
    st.dataframe(df_archive.tail(10), use_container_width=True)
    st.caption(f"Showing last 10 of {len(df_archive)} archived entries")
else:
    st.info("No archived feedback")

st.divider()

st.subheader("Model Information")
model_info = get_model_info()
if model_info.get('status') == 'Loaded':
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", "Active")
        st.metric("Type", model_info.get('type', 'Random Forest'))
    with col2:
        st.metric("Features", model_info.get('features', 'N/A'))
        st.metric("Trees", model_info.get('trees', 'N/A'))
    with col3:
        st.metric("Classes", str(model_info.get('classes', 'N/A')))
else:
    st.warning("Model is not loaded. Check your model file.")

st.caption("Developed by Naim Shaikh")