"""
Feedback Storage Module - ShopShield AI
Developed by Naim Shaikh
"""

import pandas as pd
from datetime import datetime
import os

def save_feedback_sheet(url, risk, verdict, comment=""):
    try:
        feedback_file = "data/user_feedback.csv"
        os.makedirs("data", exist_ok=True)
        feedback_entry = {
            "url": url,
            "risk_score": risk,
            "verdict": verdict,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
            try:
                df = pd.read_csv(feedback_file)
            except pd.errors.EmptyDataError:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
        df = pd.concat([df, pd.DataFrame([feedback_entry])], ignore_index=True)
        df.to_csv(feedback_file, index=False)
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False

def get_feedback_sheet():
    try:
        feedback_file = "data/user_feedback.csv"
        if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
            return pd.read_csv(feedback_file)
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
    except Exception as e:
        print(f"Error reading feedback: {e}")
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])

def get_feedback_count_sheet():
    try:
        return len(get_feedback_sheet())
    except:
        return 0