"""
Feedback Collection Module - ShopShield AI
Developed by Naim Shaikh
"""

import pandas as pd
import os
from datetime import datetime
from url_analyzer import extract_features_from_url

FEEDBACK_FILE = "data/user_feedback.csv"
FEEDBACK_ARCHIVE = "data/feedback_archive.csv"


def collect_feedback(url, ml_risk, manual_risk, final_risk, user_verdict, user_comment=""):
    try:
        features, _ = extract_features_from_url(url)
        feature_dict = features.iloc[0].to_dict()
    except:
        feature_dict = {}
    
    feedback_entry = {
        "url": url,
        "ml_risk": ml_risk,
        "manual_risk": manual_risk,
        "final_risk": final_risk,
        "user_verdict": user_verdict,
        "user_comment": user_comment,
        "timestamp": datetime.now().isoformat(),
        **feature_dict
    }
    
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame()
    if os.path.exists(FEEDBACK_FILE) and os.path.getsize(FEEDBACK_FILE) > 0:
        try:
            df = pd.read_csv(FEEDBACK_FILE)
        except pd.errors.EmptyDataError:
            pass
    df = pd.concat([df, pd.DataFrame([feedback_entry])], ignore_index=True)
    df.to_csv(FEEDBACK_FILE, index=False)
    return True


def get_feedback_summary():
    if not os.path.exists(FEEDBACK_FILE) or os.path.getsize(FEEDBACK_FILE) == 0:
        return {"total_entries": 0, "phishing_confirmed": 0, "safe_confirmed": 0, "uncertain": 0, "date_range": "No data"}
    try:
        df = pd.read_csv(FEEDBACK_FILE)
    except:
        return {"total_entries": 0, "phishing_confirmed": 0, "safe_confirmed": 0, "uncertain": 0, "date_range": "No data"}
    if df.empty:
        return {"total_entries": 0, "phishing_confirmed": 0, "safe_confirmed": 0, "uncertain": 0, "date_range": "No data"}
    return {
        "total_entries": len(df),
        "phishing_confirmed": len(df[df['user_verdict'] == 'phishing']) if 'user_verdict' in df.columns else 0,
        "safe_confirmed": len(df[df['user_verdict'] == 'safe']) if 'user_verdict' in df.columns else 0,
        "uncertain": len(df[df['user_verdict'] == 'uncertain']) if 'user_verdict' in df.columns else 0,
        "date_range": f"{df['timestamp'].min()} to {df['timestamp'].max()}" if not df.empty else "No data"
    }


def archive_feedback():
    if not os.path.exists(FEEDBACK_FILE) or os.path.getsize(FEEDBACK_FILE) == 0:
        return
    try:
        df = pd.read_csv(FEEDBACK_FILE)
    except:
        return
    if df.empty:
        return
    if os.path.exists(FEEDBACK_ARCHIVE) and os.path.getsize(FEEDBACK_ARCHIVE) > 0:
        try:
            archive_df = pd.read_csv(FEEDBACK_ARCHIVE)
            df = pd.concat([archive_df, df], ignore_index=True)
        except:
            pass
    df.to_csv(FEEDBACK_ARCHIVE, index=False)
    pd.DataFrame(columns=df.columns).to_csv(FEEDBACK_FILE, index=False)