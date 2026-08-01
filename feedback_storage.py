"""
Feedback Storage Module - ShopShield AI
Developed by Naim Shaikh
"""

import os
import pandas as pd
from datetime import datetime
import requests

FEEDBACK_FILE = "data/user_feedback.csv"
ARCHIVE_FILE = "data/feedback_archive.csv"

# Hugging Face Config
HF_TOKEN = os.getenv("HF_TOKEN")
HF_DATASET_REPO = "imnaim55/shopshield-feedback"
HF_MODEL_REPO = "imnaim55/shopshield-model"


def save_feedback(url, risk, verdict, comment=""):
    """Save user feedback locally."""
    try:
        os.makedirs("data", exist_ok=True)
        
        feedback_entry = {
            "url": url,
            "risk_score": risk,
            "verdict": verdict,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        
        if os.path.exists(FEEDBACK_FILE) and os.path.getsize(FEEDBACK_FILE) > 0:
            try:
                df = pd.read_csv(FEEDBACK_FILE)
            except:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
        
        df = pd.concat([df, pd.DataFrame([feedback_entry])], ignore_index=True)
        df.to_csv(FEEDBACK_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False


def get_feedback():
    """Get all feedback entries."""
    try:
        if os.path.exists(FEEDBACK_FILE) and os.path.getsize(FEEDBACK_FILE) > 0:
            return pd.read_csv(FEEDBACK_FILE)
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
    except:
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])


def get_feedback_count():
    """Get number of feedback entries."""
    try:
        return len(get_feedback())
    except:
        return 0


def get_archive_feedback():
    """Get archived feedback entries."""
    try:
        if os.path.exists(ARCHIVE_FILE) and os.path.getsize(ARCHIVE_FILE) > 0:
            return pd.read_csv(ARCHIVE_FILE)
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
    except:
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])


def archive_feedback():
    """Archive feedback after retraining."""
    try:
        if not os.path.exists(FEEDBACK_FILE) or os.path.getsize(FEEDBACK_FILE) == 0:
            return False
        
        df = pd.read_csv(FEEDBACK_FILE)
        if df.empty:
            return False
        
        if os.path.exists(ARCHIVE_FILE) and os.path.getsize(ARCHIVE_FILE) > 0:
            try:
                archive_df = pd.read_csv(ARCHIVE_FILE)
                df = pd.concat([archive_df, df], ignore_index=True)
            except:
                pass
        
        df.to_csv(ARCHIVE_FILE, index=False)
        pd.DataFrame(columns=df.columns).to_csv(FEEDBACK_FILE, index=False)
        return True
    except:
        return False