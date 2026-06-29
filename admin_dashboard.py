"""
Admin Dashboard - ShopShield AI
Developed by Naim Shaikh
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pickle
import time

st.set_page_config(
    page_title="Admin Dashboard - ShopShield AI",
    page_icon="📊",
    layout="wide"
)

# Session State Initialization
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 30

# Helper Functions
def get_feedback_summary():
    """Get summary of collected feedback."""
    feedback_file = "data/user_feedback.csv"
    
    if not os.path.exists(feedback_file) or os.path.getsize(feedback_file) == 0:
        return {
            "total_entries": 0,
            "phishing_confirmed": 0,
            "safe_confirmed": 0,
            "uncertain": 0,
            "has_data": False
        }
    
    try:
        df = pd.read_csv(feedback_file)
        if len(df) == 0:
            return {
                "total_entries": 0,
                "phishing_confirmed": 0,
                "safe_confirmed": 0,
                "uncertain": 0,
                "has_data": False
            }
        
        verdict_col = 'verdict' if 'verdict' in df.columns else 'user_verdict'
        
        return {
            "total_entries": len(df),
            "phishing_confirmed": len(df[df[verdict_col] == 'phishing']) if verdict_col in df.columns else 0,
            "safe_confirmed": len(df[df[verdict_col] == 'safe']) if verdict_col in df.columns else 0,
            "uncertain": len(df[df[verdict_col] == 'uncertain']) if verdict_col in df.columns else 0,
            "has_data": True
        }
    except:
        return {
            "total_entries": 0,
            "phishing_confirmed": 0,
            "safe_confirmed": 0,
            "uncertain": 0,
            "has_data": False
        }

def get_archive_summary():
    """Get summary of archived feedback."""
    archive_file = "data/feedback_archive.csv"
    
    if not os.path.exists(archive_file) or os.path.getsize(archive_file) == 0:
        return {"total_entries": 0}
    
    try:
        df = pd.read_csv(archive_file)
        return {"total_entries": len(df)}
    except:
        return {"total_entries": 0}

def get_model_info():
    """Get model information."""
    model_path = "models/url_phishing_model.pkl"
    
    if not os.path.exists(model_path):
        return {"status": "No model found"}
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        mod_time = os.path.getmtime(model_path)
        last_updated = datetime.fromtimestamp(mod_time)
        
        return {
            "status": "Active",
            "type": "Random Forest",
            "trees": model.n_estimators if hasattr(model, 'n_estimators') else "N/A",
            "features": model.n_features_in_ if hasattr(model, 'n_features_in_') else "N/A",
            "last_updated": last_updated.strftime("%Y-%m-%d %H:%M:%S"),
            "age_minutes": (datetime.now() - last_updated).total_seconds() / 60
        }
    except:
        return {"status": "Error loading model"}

def check_new_feedback():
    """Check if new feedback exists since last refresh."""
    feedback_file = "data/user_feedback.csv"
    
    if not os.path.exists(feedback_file) or os.path.getsize(feedback_file) == 0:
        return False
    
    try:
        df = pd.read_csv(feedback_file)
        if len(df) == 0 or 'timestamp' not in df.columns:
            return False
        
        latest = pd.to_datetime(df['timestamp'].max())
        return latest > st.session_state.last_refresh
    except:
        return False

# Sidebar
with st.sidebar:
    st.title("Admin Controls")
    
    st.subheader("Auto-Refresh")
    st.session_state.auto_refresh = st.toggle(
        "Enable Auto-Refresh",
        value=st.session_state.auto_refresh
    )
    
    if st.session_state.auto_refresh:
        st.session_state.refresh_interval = st.slider(
            "Refresh Interval (seconds)",
            min_value=5,
            max_value=120,
            value=st.session_state.refresh_interval,
            step=5
        )
    
    st.divider()
    
    if st.button("Refresh Now", use_container_width=True):
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    st.divider()
    
    if st.button("Force Retrain", use_container_width=True):
        with st.spinner("Retraining model..."):
            try:
                from auto_train import auto_retrain
                if auto_retrain(min_samples=1, force=True):
                    st.success("Model retrained successfully!")
                    st.session_state.last_refresh = datetime.now()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Retraining failed")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.divider()
    
    archive_stats = get_archive_summary()
    st.caption(f"Archived Feedback: {archive_stats['total_entries']} entries")
    st.caption(f"Last Refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    
    if check_new_feedback():
        st.success("New feedback detected!")
    
    st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Auto-Refresh Logic
if st.session_state.auto_refresh:
    time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
    if time_since_refresh >= st.session_state.refresh_interval:
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    remaining = int(st.session_state.refresh_interval - time_since_refresh)
    if remaining > 0:
        st.caption(f"Auto-refresh in {remaining} seconds")

# Main Dashboard
st.title("Admin Dashboard")

# Get data
summary = get_feedback_summary()
archive_stats = get_archive_summary()
model_info = get_model_info()
has_new = check_new_feedback()

if has_new:
    st.success("New feedback has been collected!")

# Metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Current Feedback",
        summary['total_entries'],
        delta="New" if has_new and summary['total_entries'] > 0 else None
    )
with col2:
    st.metric("Phishing", summary['phishing_confirmed'])
with col3:
    st.metric("Safe", summary['safe_confirmed'])
with col4:
    st.metric("Uncertain", summary['uncertain'])
with col5:
    st.metric("Archived", archive_stats['total_entries'])

# Retraining progress
if summary['total_entries'] >= 5:
    st.success(f"{summary['total_entries']} feedback entries ready for retraining!")
    st.progress(min(summary['total_entries'] / 10, 1.0))
else:
    st.info(f"{summary['total_entries']}/5 feedback entries needed for retraining")
    st.progress(summary['total_entries'] / 5)

st.divider()

# Current Feedback
st.subheader("Current Feedback")

feedback_file = "data/user_feedback.csv"
if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
    try:
        df = pd.read_csv(feedback_file)
        if len(df) > 0:
            display_cols = ['url', 'risk_score', 'verdict', 'timestamp']
            available = [col for col in display_cols if col in df.columns]
            
            if available:
                display_df = df[available].copy()
                rename_map = {
                    'url': 'URL',
                    'risk_score': 'Risk Score',
                    'verdict': 'Verdict',
                    'timestamp': 'Timestamp'
                }
                display_df = display_df.rename(columns={k: v for k, v in rename_map.items() if k in display_df.columns})
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    column_config={
                        "URL": st.column_config.TextColumn("URL", width="large"),
                        "Risk Score": st.column_config.NumberColumn("Risk Score", format="%.1f%%"),
                        "Verdict": st.column_config.TextColumn("Verdict"),
                        "Timestamp": st.column_config.TextColumn("Time")
                    }
                )
                st.caption(f"Showing {len(df)} current feedback entries")
            else:
                st.info("No feedback data available")
        else:
            st.info("No feedback waiting")
    except:
        st.info("No feedback data available")
else:
    st.info("No feedback file found")

st.divider()

# Archived Feedback
st.subheader("Archived Feedback")

archive_file = "data/feedback_archive.csv"
if os.path.exists(archive_file) and os.path.getsize(archive_file) > 0:
    try:
        df_archive = pd.read_csv(archive_file)
        if len(df_archive) > 0:
            st.write(f"Total archived: {len(df_archive)} entries")
            
            display_cols = ['url', 'risk_score', 'verdict', 'timestamp']
            available = [col for col in display_cols if col in df_archive.columns]
            
            if available:
                display_df = df_archive.tail(10)[available].copy()
                rename_map = {
                    'url': 'URL',
                    'risk_score': 'Risk Score',
                    'verdict': 'Verdict',
                    'timestamp': 'Archived Date'
                }
                display_df = display_df.rename(columns={k: v for k, v in rename_map.items() if k in display_df.columns})
                
                st.dataframe(display_df, use_container_width=True)
                st.caption(f"Showing last 10 of {len(df_archive)} archived entries")
            else:
                st.info("No archived data available")
        else:
            st.info("No archived feedback")
    except:
        st.info("No archived feedback available")
else:
    st.info("No archived feedback")

st.divider()

# Analytics Charts
st.subheader("Analytics")

if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
    try:
        df = pd.read_csv(feedback_file)
        if len(df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Risk Score Distribution")
                if 'risk_score' in df.columns:
                    bins = [0, 30, 70, 100]
                    labels = ['Low (0-30)', 'Medium (30-70)', 'High (70-100)']
                    df['risk_category'] = pd.cut(df['risk_score'], bins=bins, labels=labels, include_lowest=True)
                    st.bar_chart(df['risk_category'].value_counts())
                else:
                    st.info("No risk score data")
            
            with col2:
                st.subheader("Verdict Distribution")
                verdict_col = 'verdict' if 'verdict' in df.columns else 'user_verdict'
                if verdict_col in df.columns:
                    st.bar_chart(df[verdict_col].value_counts())
                else:
                    st.info("No verdict data")
    except:
        pass

st.divider()

# Model Information
st.subheader("Model Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Status", model_info.get('status', 'Unknown'))
    st.metric("Model Type", model_info.get('type', 'N/A'))

with col2:
    st.metric("Number of Trees", model_info.get('trees', 'N/A'))
    st.metric("Features Used", model_info.get('features', 'N/A'))

with col3:
    st.metric("Last Updated", model_info.get('last_updated', 'Never'))
    if 'age_minutes' in model_info:
        age = model_info['age_minutes']
        st.metric("Age", f"{int(age)} minutes ago" if age < 60 else f"{int(age/60)} hours ago")

# Auto-refresh indicator
if st.session_state.auto_refresh:
    st.caption(f"Auto-refresh enabled - Updates every {st.session_state.refresh_interval} seconds")
else:
    st.caption("Auto-refresh disabled - Click 'Refresh Now' to update")

# Auto-Refresh JavaScript
if st.session_state.auto_refresh:
    st.markdown(f"""
    <meta http-equiv="refresh" content="{st.session_state.refresh_interval}">
    <script>
        setTimeout(function() {{
            location.reload();
        }}, {st.session_state.refresh_interval * 1000});
    </script>
    """, unsafe_allow_html=True)

# Info Section
with st.expander("About Auto-Refresh & Auto-Retraining"):
    st.write("""
    **Auto-Refresh:**
    - Dashboard updates automatically at configured intervals
    - Shows when new feedback is collected
    - Real-time metric updates
    
    **Auto-Retraining Process:**
    1. Users submit feedback via the app
    2. Feedback saved to data/user_feedback.csv
    3. Triggers when 5+ feedback entries exist
    4. Model retrains with new feedback
    5. Feedback moves to data/feedback_archive.csv
    6. Updated model saved to models/url_phishing_model.pkl
    
    **Current Status:**
    - Auto-refresh: {'Enabled' if st.session_state.auto_refresh else 'Disabled'}
    - Auto-retraining: Active (triggers at 5 feedback entries)
    - Feedback waiting: {summary['total_entries']} entries
    """)

st.caption("Developed by Naim Shaikh")