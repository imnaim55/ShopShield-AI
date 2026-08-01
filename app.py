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
.dark-pattern-high {
    background-color: #dc3545;
    color: white;
    padding: 10px;
    border-radius: 8px;
    margin: 5px 0;
}
.dark-pattern-medium {
    background-color: #ff9800;
    color: white;
    padding: 10px;
    border-radius: 8px;
    margin: 5px 0;
}
.dark-pattern-low {
    background-color: #ffc107;
    color: #333;
    padding: 10px;
    border-radius: 8px;
    margin: 5px 0;
}
.metric-card {
    background: var(--secondary-background-color);
    padding: 15px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Session State
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


# Auto-Retrain Check
def check_and_auto_retrain():
    try:
        from auto_train import auto_retrain
        feedback_count = get_feedback_count()
        
        if feedback_count >= 5 and not st.session_state.auto_retrain_done:
            print(f"Auto-retraining triggered with {feedback_count} feedback entries")
            success = auto_retrain(min_samples=1, force=True)
            if success:
                st.session_state.auto_retrain_done = True
                st.session_state.retrain_success_time = time.strftime("%Y-%m-%d %H:%M:%S")
                print("Auto-retraining completed successfully")
                st.rerun()
    except Exception as e:
        print(f"Auto-retrain error: {e}")

# Run auto-retrain check
if not st.session_state.auto_retrain_done:
    check_and_auto_retrain()


# Dark Pattern Analysis Function
def analyze_dark_patterns(text):
    patterns = {
        "Urgency Scarcity": {
            "keywords": ["only", "limited", "hurry", "urgent", "immediate", "last chance", 
                        "ends soon", "while supplies last", "limited time", "act now", "don't miss"],
            "severity": "high"
        },
        "Social Proof": {
            "keywords": ["best seller", "most popular", "trending", "top rated", "recommended", 
                        "customers love", "bestseller", "people also bought", "trending now"],
            "severity": "medium"
        },
        "Deceptive Pricing": {
            "keywords": ["free", "discount", "exclusive", "offer", "deal", "save", "bargain", 
                        "special price", "clearance", "markdown", "sale"],
            "severity": "high"
        },
        "Forced Action": {
            "keywords": ["buy now", "subscribe", "register", "sign up", "create account", 
                        "verify now", "confirm", "act immediately", "don't delay"],
            "severity": "medium"
        },
        "Misdirection": {
            "keywords": ["click here", "learn more", "see details", "terms apply", "conditions apply", 
                        "hidden", "fine print", "disclaimer"],
            "severity": "low"
        },
        "Bait and Switch": {
            "keywords": ["free trial", "risk free", "money back", "guarantee", "bonus", 
                        "limited offer", "exclusive deal"],
            "severity": "high"
        }
    }
    
    found_patterns = {}
    lower_text = text.lower()
    total_score = 0
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    
    for category, data in patterns.items():
        matches = [w for w in data["keywords"] if w in lower_text]
        if matches:
            found_patterns[category] = {
                "matches": matches,
                "count": len(matches),
                "severity": data["severity"]
            }
            severity_counts[data["severity"]] += len(matches)
            
            if data["severity"] == "high":
                total_score += len(matches) * 3
            elif data["severity"] == "medium":
                total_score += len(matches) * 2
            else:
                total_score += len(matches) * 1
    
    return found_patterns, total_score, severity_counts


# Sidebar
with st.sidebar:
    st.title("ShopShield AI")
    
    if st.button("URL Analyzer", use_container_width=True):
        st.session_state.page = 'main'
        st.session_state.show_results = False
        st.rerun()
    
    if st.button("Admin Dashboard", use_container_width=True):
        st.session_state.page = 'admin'
        st.rerun()
    
    st.divider()
    
    url_input = st.text_input(
        "Website URL", 
        placeholder="https://example.com",
        key="url_input_main",
        value=st.session_state.get('url_input_main', '')
    )
    
    text_input = st.text_area(
        "Website Content (Optional)", 
        height=100, 
        placeholder="Paste website text for dark pattern detection...",
        key="text_input_main",
        value=st.session_state.get('text_input_main', '')
    )
    
    analyze = st.button("Analyze Website", use_container_width=True, key="analyze_btn")
    
    if analyze and url_input.strip():
        st.session_state.current_url = url_input
        st.session_state.current_text = text_input if text_input.strip() else st.session_state.current_text
        st.session_state.show_results = True
        st.rerun()
    
    st.divider()
    feedback_count = get_feedback_count()
    st.caption(f"Feedback entries: {feedback_count}")
    if feedback_count >= 5:
        st.success("Auto-retraining ready")
    st.caption("Detects phishing using ML + heuristics")


# Main Page
if st.session_state.page == 'main':
    
    if not st.session_state.show_results:
        st.title("ShopShield AI")
        st.subheader("AI-Powered Phishing Detection")
        st.write("Enter a URL in the sidebar and click 'Analyze Website' to check if it is safe or a phishing attempt.")
        
        with st.expander("Example URLs to Test"):
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
        
        st.title("Security Analysis Report")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Phishing Risk", f"{risk:.2f}%")
        col2.metric("Risk Level", risk_level)
        col3.metric("Verdict", verdict)
        
        st.progress(int(risk))
        st.markdown(f'<div class="risk-box" style="background:{color}">Overall Risk: {risk:.2f}%</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("URL Details")
        st.code(current_url)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Length", len(current_url))
        col2.metric("HTTPS", "Yes" if current_url.startswith("https://") else "No")
        col3.metric("Hyphens", current_url.count("-"))
        col4.metric("Dots", current_url.count("."))
        
        st.divider()
        
        # Enhanced Dark Pattern Analysis
        st.subheader("Dark Pattern Analysis")
        
        if not current_text.strip():
            st.info("No website content provided for dark pattern analysis.")
            st.info("Tip: Paste website text in the sidebar for dark pattern detection.")
        else:
            found_patterns, total_score, severity_counts = analyze_dark_patterns(current_text)
            
            if found_patterns:
                st.error("Dark Patterns Detected")
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f'<div class="metric-card"><strong>Total Score</strong><br><span style="font-size:24px;">{total_score}</span></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric-card"><strong>High Severity</strong><br><span style="font-size:24px;color:#dc3545;">{severity_counts["high"]}</span></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="metric-card"><strong>Medium Severity</strong><br><span style="font-size:24px;color:#ff9800;">{severity_counts["medium"]}</span></div>', unsafe_allow_html=True)
                
                st.write("Detailed Analysis:")
                
                for category, data in found_patterns.items():
                    severity_class = "dark-pattern-high" if data["severity"] == "high" else "dark-pattern-medium" if data["severity"] == "medium" else "dark-pattern-low"
                    severity_label = "HIGH" if data["severity"] == "high" else "MEDIUM" if data["severity"] == "medium" else "LOW"
                    
                    with st.expander(f"{category} ({data['count']} matches - {severity_label} severity)"):
                        st.markdown(f'<div class="{severity_class}">Found {data["count"]} suspicious phrases:</div>', unsafe_allow_html=True)
                        for item in data["matches"]:
                            st.write(f"- {item}")
                
                # Risk assessment
                if total_score > 20:
                    st.error("High risk of dark patterns detected. This website may be using deceptive tactics.")
                elif total_score > 10:
                    st.warning("Some dark patterns detected. Exercise caution when interacting with this website.")
                else:
                    st.info("Minor dark pattern indicators found. Review the details above.")
            else:
                st.success("No obvious dark patterns detected in the provided text.")
                st.caption("The text appears to be free from common deceptive patterns.")
        
        st.divider()
        
        st.subheader("Help Improve ShopShield AI")
        st.write("Was this analysis correct? Your feedback helps train the model.")
        
        if st.session_state.feedback_success:
            if st.session_state.feedback_success:
                st.success(st.session_state.feedback_message)
            else:
                st.error(st.session_state.feedback_message)
            st.session_state.feedback_success = None
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Yes - Safe", use_container_width=True):
                if save_feedback(current_url, risk, "safe"):
                    st.session_state.feedback_success = True
                    st.session_state.feedback_message = "Thank you for your feedback!"
                    st.session_state.auto_retrain_done = False
                    st.rerun()
        with col2:
            if st.button("Yes - Phishing", use_container_width=True):
                if save_feedback(current_url, risk, "phishing"):
                    st.session_state.feedback_success = True
                    st.session_state.feedback_message = "Thank you for your feedback!"
                    st.session_state.auto_retrain_done = False
                    st.rerun()
        with col3:
            if st.button("Not Sure", use_container_width=True):
                if save_feedback(current_url, risk, "uncertain"):
                    st.session_state.feedback_success = True
                    st.session_state.feedback_message = "Feedback recorded as uncertain."
                    st.session_state.auto_retrain_done = False
                    st.rerun()
        
        if st.button("New Analysis", use_container_width=True):
            st.session_state.show_results = False
            st.session_state.current_url = ""
            st.session_state.current_text = ""
            st.session_state.risk_score = None
            st.session_state.feedback_success = None
            st.rerun()
        
        st.caption("Developed by Naim Shaikh")


# Admin Dashboard
else:
    if not st.session_state.admin_logged_in:
        st.title("Admin Login")
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
        from auto_train import auto_retrain
        from feedback_storage import get_feedback, get_archive_feedback
        from url_analyzer import get_model_info
        from datetime import datetime
        import time
        
        if 'retrain_success_time' not in st.session_state:
            st.session_state.retrain_success_time = None
        
        st.title("Admin Dashboard")
        
        with st.sidebar:
            st.write(f"Logged in as: admin")
            if st.button("Logout", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.rerun()
            
            st.divider()
            
            feedback_count = get_feedback_count()
            if feedback_count >= 5:
                st.success("Auto-retraining will trigger on next page load")
            else:
                st.info(f"{feedback_count}/5 feedback needed for auto-retrain")
            
            st.divider()
            
            if st.button("Force Retrain (Manual)", use_container_width=True):
                with st.spinner("Retraining model..."):
                    try:
                        if auto_retrain(min_samples=1, force=True):
                            st.session_state.retrain_success_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state.auto_retrain_done = True
                            st.success(f"Model retrained successfully at {st.session_state.retrain_success_time}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Retraining failed. Check logs.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        feedback_count = get_feedback_count()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Feedback", feedback_count)
        with col2:
            st.metric("Ready for Retraining", "Yes" if feedback_count >= 5 else "No")
        with col3:
            st.metric("Last Retrain", st.session_state.retrain_success_time or "Never")
        
        if feedback_count >= 5:
            st.success(f"{feedback_count} feedback entries ready for retraining!")
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
        if model_info and model_info.get('status') == 'Loaded':
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
            st.info("Run 'python create_model.py' to create an initial model.")
        
        st.caption("Developed by Naim Shaikh")