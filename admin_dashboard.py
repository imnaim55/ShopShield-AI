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
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
    .admin-header {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
    }
    .admin-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .admin-header p {
        color: #a0aec0;
        margin: 0;
    }
    .admin-metric {
        background: var(--secondary-background-color);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        text-align: center;
        transition: all 0.3s;
    }
    .admin-metric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .admin-metric .label {
        font-size: 0.85rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .admin-metric .value {
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .status-badge.success {
        background: #28a74520;
        color: #28a745;
        border: 1px solid #28a74540;
    }
    .status-badge.warning {
        background: #ff980020;
        color: #ff9800;
        border: 1px solid #ff980040;
    }
    .status-badge.info {
        background: #17a2b820;
        color: #17a2b8;
        border: 1px solid #17a2b840;
    }
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3a7bd5;
        display: inline-block;
    }
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #888;
        font-size: 0.9rem;
        border-top: 1px solid var(--border-color);
        margin-top: 2rem;
    }
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 20px;
        max-width: 500px;
        margin: 0 auto;
    }
    .login-container h1 {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }
    .login-container p {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    .login-container hr {
        margin: 20px 0 30px 0;
        width: 100%;
    }
    .sidebar-admin {
        padding: 1rem 0;
    }
    .sidebar-admin .user-info {
        text-align: center;
        padding: 10px;
        background: var(--secondary-background-color);
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'retrain_success_time' not in st.session_state:
    st.session_state.retrain_success_time = None


def get_indian_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)


def login_page():
    st.markdown("""
    <div class="login-container">
        <h1>Admin Login</h1>
        <p>Enter your credentials to access the admin dashboard.</p>
        <hr>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        username = st.text_input("Username", placeholder="Enter username", key="login_user")
        password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")
        
        if st.button("Login", width="stretch"):
            if username == "admin" and password == "ShopShield2024!":
                st.session_state.admin_logged_in = True
                st.session_state.admin_username = username
                st.rerun()
            else:
                st.error("Invalid credentials")


if not st.session_state.admin_logged_in:
    login_page()
    st.stop()

st.markdown("""
<div class="admin-header">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <h1>Admin Dashboard</h1>
            <p>Monitor feedback, manage model retraining, and view analytics</p>
        </div>
        <div style="text-align:right;">
            <span style="color:#a0aec0;">admin</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-admin">', unsafe_allow_html=True)
    st.markdown("""
    <div class="user-info">
        <div style="font-size:2rem;">👤</div>
        <div style="font-weight:600;">Admin</div>
        <div style="font-size:0.8rem;color:#888;">Logged in</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Logout", width="stretch"):
        st.session_state.admin_logged_in = False
        st.rerun()
    
    st.divider()
    
    st.markdown("### Model Management")
    
    feedback_count = get_feedback_count()
    if feedback_count >= 5:
        st.success(f"✅ {feedback_count} feedback entries ready for retraining")
    else:
        st.info(f"📝 {feedback_count}/5 feedback needed for auto-retrain")
    
    st.divider()
    
    if st.button("Force Retrain", width="stretch"):
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
    
    st.divider()
    st.caption("ShopShield AI v1.0")
    st.caption("Developed by Naim Shaikh")

feedback_count = get_feedback_count()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="admin-metric">
        <div class="label">Current Feedback</div>
        <div class="value">{feedback_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if feedback_count >= 5:
        status_class = "success"
        status_text = "Ready"
    elif feedback_count > 0:
        status_class = "warning"
        status_text = f"Collecting ({feedback_count}/5)"
    else:
        status_class = "info"
        status_text = "Waiting"
    
    st.markdown(f"""
    <div class="admin-metric">
        <div class="label">Retraining Status</div>
        <div class="value"><span class="status-badge {status_class}">{status_text}</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    last_train = st.session_state.retrain_success_time or "Never"
    st.markdown(f"""
    <div class="admin-metric">
        <div class="label">Last Retrain</div>
        <div class="value" style="font-size:1.2rem;">{last_train}</div>
    </div>
    """, unsafe_allow_html=True)

if feedback_count >= 5:
    st.success(f"✅ {feedback_count} feedback entries ready for retraining!")
    st.progress(min(feedback_count / 10, 1.0))
elif feedback_count > 0:
    st.info(f"📝 {feedback_count}/5 feedback entries needed for retraining")
    st.progress(feedback_count / 5)
else:
    st.info("📝 No feedback collected yet. Submit feedback from the main app to train the model.")
    st.progress(0.0)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">Current Feedback</div>', unsafe_allow_html=True)
    df_feedback = get_feedback()
    if not df_feedback.empty:
        st.dataframe(df_feedback.tail(10), use_container_width=True)
        st.caption(f"Showing last 10 of {len(df_feedback)} entries")
    else:
        st.info("No feedback collected yet")

with col2:
    st.markdown('<div class="section-title">Archived Feedback</div>', unsafe_allow_html=True)
    df_archive = get_archive_feedback()
    if not df_archive.empty:
        st.dataframe(df_archive.tail(10), use_container_width=True)
        st.caption(f"Showing last 10 of {len(df_archive)} archived entries")
    else:
        st.info("No archived feedback")

st.divider()

st.markdown('<div class="section-title">Model Information</div>', unsafe_allow_html=True)
model_info = get_model_info()
if model_info and model_info.get('status') == 'Loaded':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="admin-metric">
            <div class="label">Status</div>
            <div class="value" style="color:#28a745;font-size:1.3rem;">Active</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="admin-metric">
            <div class="label">Type</div>
            <div class="value" style="font-size:1.1rem;">{model_info.get('type', 'Random Forest')}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="admin-metric">
            <div class="label">Features</div>
            <div class="value" style="font-size:1.1rem;">{model_info.get('features', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="admin-metric">
            <div class="label">Trees</div>
            <div class="value" style="font-size:1.1rem;">{model_info.get('trees', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("Model is not loaded. Check your model file.")

st.markdown('<div class="footer">Developed by Naim Shaikh</div>', unsafe_allow_html=True)