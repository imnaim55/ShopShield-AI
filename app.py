"""
ShopShield AI - Phishing Detection System
Developed by Naim Shaikh
"""

from url_analyzer import predict_url_risk
from feedback_storage import save_feedback, get_feedback_count
import streamlit as st
import time
import re

st.set_page_config(
    page_title="ShopShield AI",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
.risk-box {
    padding: 18px;
    border-radius: 12px;
    color: white;
    font-size: 22px;
    text-align: center;
    font-weight: bold;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Session State - Initialize all variables
if 'feedback_success' not in st.session_state:
    st.session_state.feedback_success = None
if 'feedback_message' not in st.session_state:
    st.session_state.feedback_message = ""
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""
if 'current_text' not in st.session_state:
    st.session_state.current_text = ""
if 'risk_score' not in st.session_state:
    st.session_state.risk_score = None
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'auto_retrain_done' not in st.session_state:
    st.session_state.auto_retrain_done = False


def analyze_url(url):
    risk = predict_url_risk(url)
    return min(100.0, float(risk if risk is not None else 0.0))


# ======================== AUTO-RETRAIN ON PAGE LOAD ========================
# This runs every time the page loads (including after feedback submission)
def check_and_auto_retrain():
    """Auto-retrain if 5+ feedback entries exist and not done in this session."""
    try:
        from auto_train import auto_retrain
        feedback_count = get_feedback_count()
        
        # Only retrain if 5+ feedback and not done yet in this session
        if feedback_count >= 5 and not st.session_state.auto_retrain_done:
            print(f"🔄 Auto-retraining triggered! ({feedback_count} feedback entries)")
            success = auto_retrain(min_samples=1, force=True)
            if success:
                st.session_state.auto_retrain_done = True
                st.session_state.retrain_success_time = time.strftime("%Y-%m-%d %H:%M:%S")
                print("✅ Auto-retraining completed successfully!")
                # Rerun to show updated state
                st.rerun()
            else:
                print("❌ Auto-retraining failed")
    except Exception as e:
        print(f"❌ Auto-retrain error: {e}")

# Run auto-retrain check on page load (only if not already done in this session)
if not st.session_state.auto_retrain_done:
    check_and_auto_retrain()


# ======================== SIDEBAR ========================
with st.sidebar:
    st.title("🛡️ ShopShield AI")
    
    if st.button("🔍 URL Analyzer", use_container_width=True):
        st.session_state.page = 'main'
        st.session_state.show_results = False
        st.rerun()
    
    if st.button("📊 Admin Dashboard", use_container_width=True):
        st.session_state.page = 'admin'
        st.rerun()
    
    st.divider()
    
    # URL Input - Always show in sidebar
    url_input = st.text_input(
        "Website URL", 
        placeholder="https://example.com",
        key="url_input_main",
        value=st.session_state.get('url_input_main', '')
    )
    
    text_input = st.text_area(
        "Website Content (Optional)", 
        height=100, 
        placeholder="Paste website text...",
        key="text_input_main",
        value=st.session_state.get('text_input_main', '')
    )
    
    analyze = st.button("Analyze Website", use_container_width=True, key="analyze_btn")
    
    if analyze and url_input.strip():
        st.session_state.current_url = url_input
        st.session_state.current_text = text_input
        st.session_state.show_results = True
        st.rerun()
    
    st.divider()
    feedback_count = get_feedback_count()
    st.caption(f"📝 Feedback entries: {feedback_count}")
    if feedback_count >= 5:
        st.success("🔄 Auto-retraining ready!")
    st.caption("🤖 Detects phishing using ML + heuristics")


# ======================== MAIN PAGE ========================
if st.session_state.page == 'main':
    
    if not st.session_state.show_results:
        st.title("🛡️ ShopShield AI")
        st.subheader("AI-Powered Phishing Detection")
        st.write("Enter a URL in the sidebar and click 'Analyze Website' to check if it's safe or a phishing attempt.")
        
        with st.expander("📋 Example URLs to Test"):
            st.code("http://103.20.213.34:8080/free-shop-login")
            st.code("http://192.168.1.1/login")
            st.code("https://secure-paypal-verify.xyz")
            st.code("https://www.amazon.com")
            st.code("https://www.google.com")
        
        st.caption("Developed by Naim Shaikh")
    
    if st.session_state.show_results:
        current_url = st.session_state.get('current_url', '')
        current_text = st.session_state.get('current_text', '')
        
        if not current_url.strip():
            st.warning("Please enter a URL in the sidebar and click 'Analyze Website'.")
            if st.button("Back", key="back_btn"):
                st.session_state.show_results = False
                st.rerun()
            st.stop()
        
        with st.spinner("Analyzing URL..."):
            time.sleep(0.5)
            risk = analyze_url(current_url)
            st.session_state.risk_score = risk
        
        if risk < 30:
            risk_level, verdict, color = "Low", "Safe", "#28a745"
        elif risk < 70:
            risk_level, verdict, color = "Medium", "Suspicious", "#ff9800"
        else:
            risk_level, verdict, color = "High", "Phishing Detected", "#dc3545"
        
        st.title("📊 Security Analysis Report")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Phishing Risk", f"{risk:.2f}%")
        col2.metric("Risk Level", risk_level)
        col3.metric("Verdict", verdict)
        
        st.progress(int(risk))
        st.markdown(f'<div class="risk-box" style="background:{color}">Overall Risk: {risk:.2f}%</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("🌐 URL Details")
        st.code(current_url)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Length", len(current_url))
        col2.metric("HTTPS", "Yes" if current_url.startswith("https://") else "No")
        col3.metric("Hyphens", current_url.count("-"))
        col4.metric("Dots", current_url.count("."))
        
        st.divider()
        
        st.subheader("🎯 Dark Pattern Analysis")
        if not current_text.strip():
            st.info("No website content provided for dark pattern analysis.")
        else:
            patterns = {
                "Urgency": ["only", "limited", "hurry", "urgent", "immediate", "last chance"],
                "Social Proof": ["best seller", "most popular", "trending", "top rated"],
                "Deceptive Pricing": ["free", "discount", "exclusive", "offer", "deal", "save"],
                "Forced Action": ["buy now", "subscribe", "sign up", "create account", "verify now"],
                "Misdirection": ["click here", "learn more", "terms apply", "conditions apply"]
            }
            found_patterns = {}
            lower_text = current_text.lower()
            for category, keywords in patterns.items():
                matches = [w for w in keywords if w in lower_text]
                if matches:
                    found_patterns[category] = matches
            
            if found_patterns:
                st.warning("⚠️ Potential dark patterns detected")
                for category, matches in found_patterns.items():
                    with st.expander(f"{category} ({len(matches)} matches)"):
                        for item in matches:
                            st.write(f"- {item}")
            else:
                st.success("✅ No obvious dark patterns detected")
        
        st.divider()
        
        st.subheader("📝 Help Improve ShopShield AI")
        st.write("Was this analysis correct? Your feedback helps train the model.")
        
        if st.session_state.feedback_success:
            if st.session_state.feedback_success:
                st.success(st.session_state.feedback_message)
            else:
                st.error(st.session_state.feedback_message)
            st.session_state.feedback_success = None
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Yes - Safe", use_container_width=True):
                if save_feedback(current_url, risk, "safe"):
                    st.session_state.feedback_success = True
                    st.session_state.feedback_message = "Thank you for your feedback!"
                    st.session_state.auto_retrain_done = False  # Reset for auto-retrain
                    st.rerun()
        with col2:
            if st.button("❌ Yes - Phishing", use_container_width=True):
                if save_feedback(current_url, risk, "phishing"):
                    st.session_state.feedback_success = True
                    st.session_state.feedback_message = "Thank you for your feedback!"
                    st.session_state.auto_retrain_done = False  # Reset for auto-retrain
                    st.rerun()
        with col3:
            if st.button("❓ Not Sure", use_container_width=True):
                if save_feedback(current_url, risk, "uncertain"):
                    st.session_state.feedback_success = True
                    st.session_state.feedback_message = "Feedback recorded as uncertain."
                    st.session_state.auto_retrain_done = False  # Reset for auto-retrain
                    st.rerun()
        
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.show_results = False
            st.session_state.current_url = ""
            st.session_state.current_text = ""
            st.session_state.risk_score = None
            st.session_state.feedback_success = None
            st.rerun()
        
        st.caption("Developed by Naim Shaikh")


# ======================== ADMIN DASHBOARD ========================
else:
    # Admin Login
    if not st.session_state.admin_logged_in:
        st.title("🔐 Admin Login")
        st.write("Enter your credentials to access the admin dashboard.")
        
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("---")
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            if st.button("Login", use_container_width=True):
                if username == "admin" and password == "ShopShield2024!":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    else:
        # Admin Dashboard Content
        from auto_train import auto_retrain
        from feedback_storage import get_feedback, get_archive_feedback
        from url_analyzer import get_model_info
        from datetime import datetime
        import time
        
        if 'retrain_success_time' not in st.session_state:
            st.session_state.retrain_success_time = None
        
        st.title("📊 Admin Dashboard")
        
        # Sidebar Controls
        with st.sidebar:
            st.write(f"👤 Logged in as: **admin**")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.rerun()
            
            st.divider()
            
            # Show auto-retrain status
            feedback_count = get_feedback_count()
            if feedback_count >= 5:
                st.success("✅ Auto-retraining will trigger on next page load")
            else:
                st.info(f"⏳ {feedback_count}/5 feedback needed for auto-retrain")
            
            st.divider()
            
            if st.button("🔄 Force Retrain (Manual)", use_container_width=True):
                with st.spinner("Retraining model..."):
                    try:
                        if auto_retrain(min_samples=1, force=True):
                            st.session_state.retrain_success_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state.auto_retrain_done = True
                            st.success(f"✅ Model retrained successfully at {st.session_state.retrain_success_time}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Retraining failed. Check logs.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Metrics
        feedback_count = get_feedback_count()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Current Feedback", feedback_count)
        with col2:
            st.metric("🔄 Ready for Retraining", "✅" if feedback_count >= 5 else "❌")
        with col3:
            st.metric("⏰ Last Retrain", st.session_state.retrain_success_time or "Never")
        
        if feedback_count >= 5:
            st.success(f"✅ {feedback_count} feedback entries ready for retraining!")
            st.progress(min(feedback_count / 10, 1.0))
        else:
            st.info(f"⏳ {feedback_count}/5 feedback entries needed for retraining")
            st.progress(feedback_count / 5)
        
        st.divider()
        
        # Current Feedback
        st.subheader("📋 Current Feedback")
        df_feedback = get_feedback()
        if not df_feedback.empty:
            st.dataframe(df_feedback.tail(10), use_container_width=True)
            st.caption(f"Showing last 10 of {len(df_feedback)} entries")
        else:
            st.info("No feedback collected yet")
        
        # Archived Feedback
        st.divider()
        st.subheader("📦 Archived Feedback")
        df_archive = get_archive_feedback()
        if not df_archive.empty:
            st.dataframe(df_archive.tail(10), use_container_width=True)
            st.caption(f"Showing last 10 of {len(df_archive)} archived entries")
        else:
            st.info("No archived feedback")
        
        # Model Information
        st.divider()
        st.subheader("🤖 Model Information")
        model_info = get_model_info()
        if model_info and model_info.get('status') == 'Loaded':
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status", "✅ Active")
                st.metric("Type", model_info.get('type', 'Random Forest'))
            with col2:
                st.metric("Features", model_info.get('features', 'N/A'))
                st.metric("Trees", model_info.get('trees', 'N/A'))
            with col3:
                st.metric("Classes", str(model_info.get('classes', 'N/A')))
        else:
            st.warning("⚠️ Model is not loaded. Check your model file.")
            st.info("Run 'python create_model.py' to create an initial model.")
        
        st.caption("Developed by Naim Shaikh")