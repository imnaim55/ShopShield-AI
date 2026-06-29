"""
ShopShield AI - Phishing Detection System
Developed by Naim Shaikh
"""

from url_analyzer import predict_url_risk
import streamlit as st
import time
import re
import pandas as pd
from datetime import datetime
import os
import pickle

st.set_page_config(
    page_title="ShopShield AI",
    page_icon="🛡️",
    layout="wide",
)

st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: var(--secondary-background-color) !important;
    border-right: 1px solid var(--border-color) !important;
}
section[data-testid="stSidebar"] > div {
    background-color: var(--secondary-background-color) !important;
}
@media (prefers-color-scheme: dark) {
    section[data-testid="stSidebar"] {
        background-color: #1e1e1e !important;
        border-color: #333 !important;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #1e1e1e !important;
    }
}
@media (prefers-color-scheme: light) {
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-color: #e0e0e0 !important;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #ffffff !important;
    }
}
div[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    padding: 15px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
}
div[data-testid="stMetric"] label {
    color: var(--text-color) !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--text-color) !important;
}
.risk-box {
    padding: 18px;
    border-radius: 12px;
    color: white !important;
    font-size: 22px;
    text-align: center;
    font-weight: bold;
    margin: 10px 0;
}
.stCodeBlock {
    background: var(--secondary-background-color) !important;
    border-radius: 8px !important;
}
.streamlit-expanderHeader {
    background-color: var(--secondary-background-color) !important;
    border-radius: 5px !important;
}
</style>
""", unsafe_allow_html=True)

if 'feedback_success' not in st.session_state:
    st.session_state.feedback_success = None
if 'feedback_message' not in st.session_state:
    st.session_state.feedback_message = ""
if 'risk' not in st.session_state:
    st.session_state.risk = None
if 'url' not in st.session_state:
    st.session_state.url = None
if 'text' not in st.session_state:
    st.session_state.text = ""
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False


def save_feedback_local(feedback_entry):
    """Save feedback locally."""
    try:
        feedback_file = "data/user_feedback.csv"
        os.makedirs("data", exist_ok=True)
        
        try:
            from url_analyzer import extract_features_from_url
            features, _ = extract_features_from_url(feedback_entry["url"])
            feature_dict = features.iloc[0].to_dict()
            feedback_entry.update(feature_dict)
        except Exception as e:
            print(f"Error extracting features: {e}")
        
        if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
            try:
                df = pd.read_csv(feedback_file)
                for col in feedback_entry.keys():
                    if col not in df.columns:
                        df[col] = None
                df = pd.concat([df, pd.DataFrame([feedback_entry])], ignore_index=True)
            except pd.errors.EmptyDataError:
                df = pd.DataFrame([feedback_entry])
        else:
            df = pd.DataFrame([feedback_entry])
        
        df.to_csv(feedback_file, index=False)
        return True
    except Exception as e:
        print(f"Error saving feedback locally: {e}")
        return False


def save_feedback_cloud(feedback_entry):
    """Save feedback to GitHub for deployed app."""
    try:
        import requests
        import base64
        from io import StringIO
        
        GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
        if not GITHUB_TOKEN:
            print("GitHub token not found")
            return False
        
        REPO_OWNER = st.secrets.get("REPO_OWNER", "your-username")
        REPO_NAME = st.secrets.get("REPO_NAME", "your-repo-name")
        FILE_PATH = "data/user_feedback.csv"
        BRANCH = "main"
        
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            from url_analyzer import extract_features_from_url
            features, _ = extract_features_from_url(feedback_entry["url"])
            feature_dict = features.iloc[0].to_dict()
            feedback_entry.update(feature_dict)
        except Exception as e:
            print(f"Error extracting features: {e}")
        
        response = requests.get(url, headers=headers)
        df = pd.DataFrame()
        
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content['content']).decode('utf-8')
            df = pd.read_csv(StringIO(decoded))
            sha = content['sha']
        else:
            sha = None
        
        new_df = pd.DataFrame([feedback_entry])
        df = pd.concat([df, new_df], ignore_index=True)
        
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        content_encoded = base64.b64encode(csv_buffer.getvalue().encode('utf-8')).decode('utf-8')
        
        payload = {
            "message": "Update user feedback",
            "content": content_encoded,
            "branch": BRANCH
        }
        if sha:
            payload["sha"] = sha
        
        response = requests.put(url, headers=headers, json=payload)
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error saving feedback to GitHub: {e}")
        return False


def save_feedback(url, risk, verdict, comment=""):
    """Save user feedback for model improvement."""
    try:
        feedback_entry = {
            "url": url,
            "risk_score": risk,
            "verdict": verdict,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        
        if os.getenv("STREAMLIT_CLOUD"):
            return save_feedback_cloud(feedback_entry)
        else:
            return save_feedback_local(feedback_entry)
            
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False


def analyze_url(url):
    """Analyze URL for phishing risk."""
    risk = predict_url_risk(url)
    
    if risk is None or not isinstance(risk, (int, float)):
        risk = 0.0
    
    if risk < 10:
        manual_risk = 0
        url_lower = url.lower()
        
        if re.search(r"(\d{1,3}\.){3}\d{1,3}", url_lower):
            manual_risk += 40
        
        if any(port in url_lower for port in [":8080", ":8443", ":3000", ":5000", ":8000"]):
            manual_risk += 25
        
        suspicious_keywords = ["free", "login", "verify", "account", "secure", "payment", "wallet"]
        keyword_count = sum(1 for kw in suspicious_keywords if kw in url_lower)
        manual_risk += keyword_count * 5
        
        suspicious_paths = ["/verify", "/login", "/account", "/secure", "/confirm"]
        if any(path in url_lower for path in suspicious_paths):
            manual_risk += 10
        
        risk = max(risk, manual_risk)
    
    return min(100.0, float(risk))


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
    
    if st.session_state.page == 'main':
        url_input = st.text_input(
            "Website URL (Optional)",
            placeholder="https://example.com",
            key="url_input"
        )
        
        text_input = st.text_area(
            "Website Content (Optional)",
            height=150,
            placeholder="Paste website text for dark pattern detection...",
            key="text_input"
        )
        
        analyze = st.button("Analyze Website", use_container_width=True)
        if analyze:
            st.session_state.show_results = True
        
        # Feedback Count Display
        st.divider()
        feedback_file = "data/user_feedback.csv"
        if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
            try:
                df = pd.read_csv(feedback_file)
                feedback_count = len(df)
                st.info(f"📊 Feedback entries: {feedback_count}")
                if feedback_count >= 5:
                    st.success("✅ Ready for auto-retraining!")
                else:
                    st.warning(f"⏳ Need {5 - feedback_count} more entries for retraining")
            except Exception as e:
                st.caption("Feedback system active")
        else:
            st.caption("No feedback collected yet")
        
        st.caption("Detects phishing attempts using machine learning and heuristic analysis.")

if st.session_state.page == 'main':
    
    if not st.session_state.show_results:
        st.title("ShopShield AI")
        st.subheader("AI-Powered Phishing Detection")
        
        st.markdown("""
        ShopShield AI analyzes URLs and website content to detect phishing attempts 
        and deceptive patterns using a trained Random Forest model.
        
        **Features:**
        - URL structure analysis
        - Phishing probability detection
        - Dark pattern identification
        - User feedback collection for continuous learning
        
        **How to Use:**
        1. Enter a URL in the sidebar
        2. Optionally paste website text
        3. Click "Analyze Website" to view results
        """)
        
        with st.expander("Example URLs to Test"):
            st.code("http://103.20.213.34:8080/free-shop-login")
            st.code("http://192.168.1.1/login")
            st.code("https://www.amazon.com")
            st.code("https://www.google.com")
        
        st.caption("Developed by Naim Shaikh")

    if st.session_state.show_results:
        current_url = st.session_state.get('url_input', '')
        current_text = st.session_state.get('text_input', '')
        
        has_url = bool(current_url.strip())
        has_text = bool(current_text.strip())
        
        if not has_url and not has_text:
            st.warning("Please enter a URL or paste website content to analyze.")
            if st.button("Back"):
                st.session_state.show_results = False
                st.rerun()
            st.stop()
        
        if has_url:
            with st.spinner("Analyzing URL..."):
                time.sleep(0.5)
                risk = analyze_url(current_url)
                st.session_state.risk = risk
                st.session_state.url = current_url
        else:
            risk = 0
            st.info("Analyzing website content for dark patterns only.")
        
        if risk < 30:
            risk_level = "Low"
            verdict = "Safe"
            box_color = "#28a745"
        elif risk < 70:
            risk_level = "Medium"
            verdict = "Suspicious"
            box_color = "#ff9800"
        else:
            risk_level = "High"
            verdict = "Phishing Detected"
            box_color = "#dc3545"
        
        st.title("Security Analysis Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Phishing Risk",
                f"{risk:.2f}%" if has_url else "N/A"
            )
        
        with col2:
            st.metric(
                "Risk Level",
                risk_level if has_url else "N/A"
            )
        
        with col3:
            st.metric(
                "Verdict",
                verdict if has_url else "N/A"
            )
        
        if has_url:
            st.progress(int(risk))
            st.markdown(
                f"""
                <div class="risk-box" style="background:{box_color}; color: white;">
                    Overall Risk: {risk:.2f}%
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        st.divider()
        
        if has_url:
            st.subheader("URL Details")
            st.code(current_url, language="text")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Length", len(current_url))
            with col2:
                st.metric("HTTPS", "Yes" if current_url.startswith("https://") else "No")
            with col3:
                st.metric("Hyphens", current_url.count("-"))
            with col4:
                st.metric("Dots", current_url.count("."))
            
            st.divider()
        
        st.subheader("Dark Pattern Analysis")
        
        if not has_text:
            st.info("No website content provided for dark pattern analysis.")
        else:
            patterns = {
                "Urgency": ["only", "limited", "hurry", "urgent", "immediate", "last chance", "ends soon"],
                "Social Proof": ["best seller", "most popular", "trending", "top rated", "recommended"],
                "Deceptive Pricing": ["free", "discount", "exclusive", "offer", "deal", "save"],
                "Forced Action": ["buy now", "subscribe", "sign up", "create account", "verify now"],
                "Misdirection": ["click here", "learn more", "terms apply", "conditions apply"]
            }
            
            found_patterns = {}
            lower_text = current_text.lower()
            
            for category, keywords in patterns.items():
                matches = [word for word in keywords if word in lower_text]
                if matches:
                    found_patterns[category] = matches
            
            if found_patterns:
                st.warning("Potential dark patterns detected")
                for category, matches in found_patterns.items():
                    with st.expander(f"{category} ({len(matches)} matches)"):
                        for item in matches:
                            st.write(f"- {item}")
            else:
                st.success("No obvious dark patterns detected")
        
        st.divider()
        
        if has_url:
            st.subheader("Help Improve ShopShield AI")
            st.write("Was this analysis correct? Your feedback helps train the model.")
            
            if st.session_state.feedback_success:
                if st.session_state.feedback_success:
                    st.success(st.session_state.feedback_message)
                else:
                    st.error(st.session_state.feedback_message)
                st.session_state.feedback_success = None
                st.session_state.feedback_message = ""
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Yes - Safe", use_container_width=True):
                    if save_feedback(current_url, risk, "safe"):
                        st.session_state.feedback_success = True
                        st.session_state.feedback_message = "Thank you for your feedback!"
                        st.rerun()
            
            with col2:
                if st.button("Yes - Phishing", use_container_width=True):
                    if save_feedback(current_url, risk, "phishing"):
                        st.session_state.feedback_success = True
                        st.session_state.feedback_message = "Thank you for your feedback!"
                        st.rerun()
            
            with col3:
                if st.button("Not Sure", use_container_width=True):
                    if save_feedback(current_url, risk, "uncertain"):
                        st.session_state.feedback_success = True
                        st.session_state.feedback_message = "Feedback recorded as uncertain."
                        st.rerun()
        
        st.divider()
        if st.button("New Analysis", use_container_width=True):
            st.session_state.show_results = False
            st.session_state.feedback_success = None
            st.rerun()
        
        st.caption("Developed by Naim Shaikh")

else:
    if not st.session_state.admin_logged_in:
        st.title("Admin Login")
        st.write("Enter your credentials to access the admin dashboard.")
        
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", key="admin_user")
        with col2:
            password = st.text_input("Password", type="password", key="admin_pass")
        
        if st.button("Login", use_container_width=True):
            try:
                if username == st.secrets["admin"]["username"] and password == st.secrets["admin"]["password"]:
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception:
                if username == "admin" and password == "ShopShield2024!":
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    else:
        st.title("Admin Dashboard")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"Logged in as: **{st.session_state.admin_username}**")
        with col2:
            if st.button("Logout", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.rerun()
        
        st.divider()
        
        feedback_file = "data/user_feedback.csv"
        total = phishing = safe = uncertain = 0
        
        if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
            try:
                df = pd.read_csv(feedback_file)
                total = len(df)
                if 'verdict' in df.columns:
                    phishing = len(df[df['verdict'] == 'phishing'])
                    safe = len(df[df['verdict'] == 'safe'])
                    uncertain = len(df[df['verdict'] == 'uncertain'])
            except Exception:
                pass
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Feedback", total)
        with col2:
            st.metric("Phishing", phishing)
        with col3:
            st.metric("Safe", safe)
        with col4:
            st.metric("Uncertain", uncertain)
        
        if total >= 5:
            st.success(f"{total} feedback entries ready for retraining!")
            st.progress(min(total / 10, 1.0))
        else:
            st.info(f"{total}/5 feedback entries needed for retraining")
            st.progress(total / 5)
        
        st.divider()
        
        st.subheader("Recent Feedback")
        
        if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
            try:
                df = pd.read_csv(feedback_file)
                if len(df) > 0:
                    cols = ['url', 'risk_score', 'verdict', 'timestamp']
                    available = [c for c in cols if c in df.columns]
                    if available:
                        st.dataframe(df.tail(10)[available], use_container_width=True)
                else:
                    st.info("No feedback data")
            except Exception:
                st.info("No feedback data")
        else:
            st.info("No feedback data")
        
        st.divider()
        st.subheader("Model Information")
        
        model_path = "models/url_phishing_model.pkl"
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                
                mod_time = os.path.getmtime(model_path)
                last_updated = datetime.fromtimestamp(mod_time)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Model Type", "Random Forest")
                    st.metric("Trees", model.n_estimators if hasattr(model, 'n_estimators') else "N/A")
                with col2:
                    st.metric("Features", model.n_features_in_ if hasattr(model, 'n_features_in_') else "N/A")
                with col3:
                    st.metric("Last Updated", last_updated.strftime("%Y-%m-%d %H:%M"))
            except Exception:
                st.warning("Could not load model")
        else:
            st.warning("No model found")
        
        st.divider()
        if st.button("Force Retrain", use_container_width=True):
            with st.spinner("Retraining model..."):
                try:
                    from auto_train import auto_retrain
                    if auto_retrain(min_samples=1, force=True):
                        st.success("Model retrained successfully!")
                        st.rerun()
                    else:
                        st.error("Retraining failed")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        st.caption("Developed by Naim Shaikh")