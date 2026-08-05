"""
ShopShield AI - Phishing Detection System
Developed by Naim Shaikh
"""

from url_analyzer import predict_url_risk
from feedback_storage import save_feedback, get_feedback_count
from domain_analyzer import get_domain_summary, is_new_domain
from ssl_analyzer import get_ssl_summary
import streamlit as st
import time

st.set_page_config(
    page_title="ShopShield AI",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.2rem 0;
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .main-header p {
        color: #a0aec0;
        font-size: 1.1rem;
        margin-top: 0.3rem;
    }
    .risk-box {
        padding: 20px 25px;
        border-radius: 14px;
        color: white;
        font-size: 24px;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    .risk-box:hover {
        transform: scale(1.01);
    }
    .dark-pattern-high {
        background: linear-gradient(135deg, #dc3545, #c0392b);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 6px 0;
        border-left: 4px solid #ff6b6b;
    }
    .dark-pattern-medium {
        background: linear-gradient(135deg, #ff9800, #e67e22);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 6px 0;
        border-left: 4px solid #ffd93d;
    }
    .dark-pattern-low {
        background: linear-gradient(135deg, #ffc107, #f39c12);
        color: #333;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 6px 0;
        border-left: 4px solid #ffeb3b;
    }
    .metric-card {
        background: var(--secondary-background-color);
        padding: 18px 20px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        text-align: center;
        transition: all 0.3s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .metric-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .metric-card .label {
        font-size: 0.9rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .sidebar-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sidebar-subtitle {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    .feedback-section {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 20px 25px;
        border-radius: 12px;
        margin: 20px 0;
        color: white;
    }
    .feedback-section h3 {
        color: #fff;
        margin-bottom: 10px;
    }
    .feedback-section p {
        color: #a0aec0;
    }
    .feature-card {
        background: var(--secondary-background-color);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        text-align: center;
        transition: all 0.3s;
        height: 100%;
    }
    .feature-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transform: translateY(-3px);
    }
    .feature-card .icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .feature-card h4 {
        margin-bottom: 8px;
    }
    .feature-card p {
        color: #888;
        font-size: 0.9rem;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .section-header {
        font-size: 1.6rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3a7bd5;
        display: inline-block;
    }
    .stProgress > div > div {
        background: linear-gradient(135deg, #00d2ff, #3a7bd5) !important;
        border-radius: 10px;
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
</style>
""", unsafe_allow_html=True)

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
if 'is_dark_pattern_only' not in st.session_state:
    st.session_state.is_dark_pattern_only = False
if 'feedback_given' not in st.session_state:
    st.session_state.feedback_given = False
if 'analyzed_url' not in st.session_state:
    st.session_state.analyzed_url = ""
if 'input_url' not in st.session_state:
    st.session_state.input_url = ""
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""


def analyze_url(url):
    if not url or not url.strip():
        return 0.0
    risk = predict_url_risk(url)
    return min(100.0, float(risk if risk is not None else 0.0))


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


if not st.session_state.auto_retrain_done:
    check_and_auto_retrain()


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


with st.sidebar:
    st.markdown('<div class="sidebar-title">ShopShield AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">AI-Powered Phishing Detection</div>', unsafe_allow_html=True)
    
    st.divider()
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("Analyzer", width="stretch"):
            st.session_state.page = 'main'
            st.session_state.show_results = False
            st.session_state.input_url = ""
            st.session_state.input_text = ""
            st.rerun()
    with col_nav2:
        if st.button("Admin", width="stretch"):
            st.session_state.page = 'admin'
            st.rerun()
    
    st.divider()
    
    st.markdown("### Input Analysis")
    
    # Use a form with no submit button to handle clearing
    with st.form(key="analysis_form", clear_on_submit=True):
        url_input = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            key="url_input_main"
        )

        text_input = st.text_area(
            "Website Content",
            height=120,
            placeholder="Paste website text for dark pattern detection...",
            key="text_input_main"
        )
        
        submitted = st.form_submit_button("Analyze", width="stretch")
        
        if submitted:
            has_url = url_input.strip() if url_input else ""
            has_text = text_input.strip() if text_input else ""
            
            if not has_url and not has_text:
                st.warning("Please enter a URL or paste website content.")
            else:
                st.session_state.current_url = has_url
                st.session_state.current_text = has_text
                st.session_state.show_results = True
                st.session_state.feedback_given = False
                st.session_state.analyzed_url = has_url
                # Clear the input values from session state
                st.session_state.input_url = ""
                st.session_state.input_text = ""
                st.rerun()

    st.divider()
    
    st.markdown("### Status")
    feedback_count = get_feedback_count()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Feedback", feedback_count)
    with col2:
        if feedback_count >= 5:
            st.success("Ready")
        else:
            st.info(f"{feedback_count}/5")
    
    if feedback_count >= 5:
        st.success("Auto-retraining ready")
    
    st.caption("Detects phishing using ML + heuristics")
    st.caption("Developed by Naim Shaikh")


if st.session_state.page == 'main':
    if not st.session_state.show_results:
        st.markdown("""
        <div class="main-header">
            <h1>ShopShield AI</h1>
            <p>AI-Powered Phishing Detection & Dark Pattern Analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <p style="text-align:center;font-size:1.1rem;color:#888;margin-bottom:2rem;">
            Enter a URL or paste website content in the sidebar to analyze for phishing and deceptive patterns.
        </p>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="feature-card">
                <div class="icon">🔗</div>
                <h4>URL Analysis</h4>
                <p>Detects phishing URLs using ML + heuristic analysis</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="feature-card">
                <div class="icon">🎭</div>
                <h4>Dark Pattern Detection</h4>
                <p>Identifies deceptive UX patterns like urgency, social proof</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="feature-card">
                <div class="icon">🧠</div>
                <h4>Self-Learning</h4>
                <p>Continuously improves from user feedback</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### Example URLs to Test")
        col1, col2 = st.columns(2)
        with col1:
            st.code("http://103.20.213.34:8080/free-shop-login", language="text")
            st.code("http://192.168.1.1/login", language="text")
        with col2:
            st.code("https://secure-paypal-verify.xyz", language="text")
            st.code("https://www.amazon.com", language="text")
        
        st.markdown('<div class="footer">Developed by Naim Shaikh</div>', unsafe_allow_html=True)

    if st.session_state.show_results:
        current_url = st.session_state.get('current_url', '')
        current_text = st.session_state.get('current_text', '')
        has_url = current_url.strip()
        has_text = current_text.strip()

        if not has_url and not has_text:
            st.warning("No content to analyze.")
            if st.button("Back", key="back_btn"):
                st.session_state.show_results = False
                st.rerun()
            st.stop()

        st.markdown("""
        <div class="main-header" style="padding:0.8rem 0;margin-bottom:1.5rem;">
            <h1 style="font-size:2rem;">Security Analysis Report</h1>
        </div>
        """, unsafe_allow_html=True)

        if has_url:
            with st.spinner("Analyzing URL..."):
                time.sleep(0.5)
                risk = analyze_url(current_url)
                st.session_state.risk_score = risk
        else:
            risk = 0
            st.info("Dark Pattern Analysis only - No URL provided.")

        if has_url:
            if risk < 30:
                risk_level, verdict, color = "Low", "Safe", "#28a745"
            elif risk < 70:
                risk_level, verdict, color = "Medium", "Suspicious", "#ff9800"
            else:
                risk_level, verdict, color = "High", "Phishing Detected", "#dc3545"

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">Phishing Risk</div>
                    <div class="value" style="color:{color}">{risk:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">Risk Level</div>
                    <div class="value" style="color:{color}">{risk_level}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">Verdict</div>
                    <div class="value" style="color:{color}">{verdict}</div>
                </div>
                """, unsafe_allow_html=True)

            st.progress(int(risk))
            st.markdown(f'<div class="risk-box" style="background:{color}">Overall Risk: {risk:.2f}%</div>', unsafe_allow_html=True)

            st.divider()
            
            st.markdown("### URL Details")
            st.code(current_url, language="text")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">Length</div>
                    <div class="value" style="font-size:1.3rem;">{len(current_url)}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">HTTPS</div>
                    <div class="value" style="font-size:1.3rem;color:{'#28a745' if current_url.startswith('https://') else '#dc3545'}">
                        {'Yes' if current_url.startswith('https://') else 'No'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">Hyphens</div>
                    <div class="value" style="font-size:1.3rem;">{current_url.count('-')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">Dots</div>
                    <div class="value" style="font-size:1.3rem;">{current_url.count('.')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()

        st.markdown("### Dark Pattern Analysis")

        if not has_text:
            if has_url:
                st.info("No website content provided. Paste text in the sidebar for dark pattern analysis.")
            else:
                st.warning("Please paste some website text for dark pattern analysis.")
        else:
            found_patterns, total_score, severity_counts = analyze_dark_patterns(current_text)

            if found_patterns:
                st.error("Dark Patterns Detected")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="label">Total Score</div>
                        <div class="value" style="font-size:1.8rem;color:#ff6b6b;">{total_score}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="label">High Severity</div>
                        <div class="value" style="font-size:1.8rem;color:#dc3545;">{severity_counts["high"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="label">Medium Severity</div>
                        <div class="value" style="font-size:1.8rem;color:#ff9800;">{severity_counts["medium"]}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("#### Detailed Analysis:")
                for category, data in found_patterns.items():
                    severity_class = "dark-pattern-high" if data["severity"] == "high" else "dark-pattern-medium" if data["severity"] == "medium" else "dark-pattern-low"
                    severity_label = "HIGH" if data["severity"] == "high" else "MEDIUM" if data["severity"] == "medium" else "LOW"

                    with st.expander(f"{category} ({data['count']} matches - {severity_label} severity)"):
                        st.markdown(f'<div class="{severity_class}">Found {data["count"]} suspicious phrases:</div>', unsafe_allow_html=True)
                        for item in data["matches"]:
                            st.write(f"- {item}")

                if total_score > 20:
                    st.error("High risk of dark patterns detected. This website may be using deceptive tactics.")
                elif total_score > 10:
                    st.warning("Some dark patterns detected. Exercise caution when interacting with this website.")
                else:
                    st.info("Minor dark pattern indicators found. Review the details above.")
            else:
                st.success("No obvious dark patterns detected in the provided text.")
                st.caption("The text appears to be free from common deceptive patterns.")

        if has_url:
            st.divider()
            st.markdown("### Additional Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Domain Information")
                domain_info = get_domain_summary(current_url)
                st.info(domain_info)
                
                if is_new_domain(current_url):
                    st.warning("This domain is relatively new - exercise caution")
                else:
                    st.success("This domain has been established for some time")
            
            with col2:
                st.markdown("#### SSL Certificate")
                ssl_info = get_ssl_summary(current_url)
                if "Not installed" in ssl_info:
                    st.error(ssl_info)
                elif "Expired" in ssl_info:
                    st.error(ssl_info)
                elif "Expiring soon" in ssl_info:
                    st.warning(ssl_info)
                else:
                    st.success(ssl_info)

        if has_url and not st.session_state.feedback_given:
            st.divider()
            st.markdown("""
            <div class="feedback-section">
                <h3>Help Improve ShopShield AI</h3>
                <p>Was this analysis correct? Your feedback helps train the model.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.feedback_success:
                if st.session_state.feedback_success:
                    st.success(st.session_state.feedback_message)
                else:
                    st.error(st.session_state.feedback_message)
                st.session_state.feedback_success = None

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Yes - Safe", width="stretch", key="feedback_safe"):
                    if save_feedback(current_url, risk, "safe"):
                        st.session_state.feedback_given = True
                        st.session_state.feedback_success = True
                        st.session_state.feedback_message = "Thank you for your feedback! The model will learn from this."
                        st.session_state.auto_retrain_done = False
                        st.rerun()
            with col2:
                if st.button("Yes - Phishing", width="stretch", key="feedback_phishing"):
                    if save_feedback(current_url, risk, "phishing"):
                        st.session_state.feedback_given = True
                        st.session_state.feedback_success = True
                        st.session_state.feedback_message = "Thank you for your feedback! The model will learn from this."
                        st.session_state.auto_retrain_done = False
                        st.rerun()
            with col3:
                if st.button("Not Sure", width="stretch", key="feedback_uncertain"):
                    if save_feedback(current_url, risk, "uncertain"):
                        st.session_state.feedback_given = True
                        st.session_state.feedback_success = True
                        st.session_state.feedback_message = "Feedback recorded as uncertain."
                        st.session_state.auto_retrain_done = False
                        st.rerun()
        elif has_url and st.session_state.feedback_given:
            st.success("Thank you for your feedback! You can analyze a new URL to provide more feedback.")
            st.info("Enter a new URL and click Analyze to check another website.")

        if st.button("New Analysis", width="stretch"):
            st.session_state.show_results = False
            st.session_state.current_url = ""
            st.session_state.current_text = ""
            st.session_state.risk_score = None
            st.session_state.feedback_success = None
            st.session_state.feedback_given = False
            st.session_state.analyzed_url = ""
            st.rerun()

        st.markdown('<div class="footer">Developed by Naim Shaikh</div>', unsafe_allow_html=True)


else:
    if not st.session_state.admin_logged_in:
        st.markdown("""
        <div class="login-container">
            <h1>Admin Login</h1>
            <p>Enter your credentials to access the admin dashboard.</p>
            <hr>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            username = st.text_input("Username", placeholder="Enter username", key="admin_user")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="admin_pass")

            if st.button("Login", width="stretch", key="admin_login"):
                if username == "admin" and password == "ShopShield2024!":
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    else:
        from auto_train import auto_retrain
        from feedback_storage import get_feedback, get_archive_feedback
        from url_analyzer import get_model_info
        from datetime import datetime

        if 'retrain_success_time' not in st.session_state:
            st.session_state.retrain_success_time = None

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
        </style>
        """, unsafe_allow_html=True)

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
            st.markdown("### Admin Controls")
            
            if st.button("Dashboard", width="stretch"):
                st.rerun()
            
            st.divider()
            
            feedback_count = get_feedback_count()
            if feedback_count >= 5:
                st.success("Auto-retraining will trigger on next page load")
            else:
                st.info(f"{feedback_count}/5 feedback needed for auto-retrain")

            st.divider()
            
            st.markdown("### Model Management")
            if st.button("Force Retrain (Manual)", width="stretch"):
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
            st.markdown(f"""
            <div class="admin-metric">
                <div class="label">Current Feedback</div>
                <div class="value">{feedback_count}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            status_class = "success" if feedback_count >= 5 else "warning"
            status_text = "Ready" if feedback_count >= 5 else "Waiting"
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
            st.success(f"{feedback_count} feedback entries ready for retraining!")
            st.progress(min(feedback_count / 10, 1.0))
        else:
            st.info(f"{feedback_count}/5 feedback entries needed for retraining")
            st.progress(feedback_count / 5)

        st.divider()

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Current Feedback")
            df_feedback = get_feedback()
            if not df_feedback.empty:
                st.dataframe(df_feedback.tail(10), use_container_width=True)
                st.caption(f"Showing last 10 of {len(df_feedback)} entries")
            else:
                st.info("No feedback collected yet")

        with col2:
            st.markdown("### Archived Feedback")
            df_archive = get_archive_feedback()
            if not df_archive.empty:
                st.dataframe(df_archive.tail(10), use_container_width=True)
                st.caption(f"Showing last 10 of {len(df_archive)} archived entries")
            else:
                st.info("No archived feedback")

        st.divider()

        st.markdown("### Model Information")
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