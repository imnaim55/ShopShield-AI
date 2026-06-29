"""
Feedback Collection Module - ShopShield AI
Developed by Naim Shaikh
"""

import pandas as pd
import os
from datetime import datetime
from url_analyzer import extract_features_from_url

# Constants
FEEDBACK_FILE = "data/user_feedback.csv"
FEEDBACK_ARCHIVE = "data/feedback_archive.csv"


def collect_feedback(url, ml_risk, manual_risk, final_risk, user_verdict, user_comment=""):
    """
    Collect user feedback for future retraining.
    
    Args:
        url: The analyzed URL
        ml_risk: ML model risk score
        manual_risk: Heuristic risk score
        final_risk: Combined final risk score
        user_verdict: User's verdict (phishing/safe/uncertain)
        user_comment: Optional user comment
    
    Returns:
        bool: True if feedback saved successfully
    """
    # Extract URL features
    try:
        features, _ = extract_features_from_url(url)
        feature_dict = features.iloc[0].to_dict()
    except:
        feature_dict = {}
    
    # Create feedback entry
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
    
    # Save to CSV
    os.makedirs("data", exist_ok=True)
    
    if os.path.exists(FEEDBACK_FILE) and os.path.getsize(FEEDBACK_FILE) > 0:
        try:
            df = pd.read_csv(FEEDBACK_FILE)
            df = pd.concat([df, pd.DataFrame([feedback_entry])], ignore_index=True)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame([feedback_entry])
    else:
        df = pd.DataFrame([feedback_entry])
    
    df.to_csv(FEEDBACK_FILE, index=False)
    print(f"Feedback collected for {url}")
    
    # Notify if ready for retraining
    if len(df) >= 5:
        print("Enough feedback collected! Auto-retraining will trigger soon.")
    
    return True


def get_feedback_summary():
    """
    Get summary of collected feedback.
    
    Returns:
        dict: Feedback statistics
    """
    if not os.path.exists(FEEDBACK_FILE) or os.path.getsize(FEEDBACK_FILE) == 0:
        return {
            "total_entries": 0,
            "phishing_confirmed": 0,
            "safe_confirmed": 0,
            "uncertain": 0,
            "date_range": "No data"
        }
    
    try:
        df = pd.read_csv(FEEDBACK_FILE)
    except pd.errors.EmptyDataError:
        return {
            "total_entries": 0,
            "phishing_confirmed": 0,
            "safe_confirmed": 0,
            "uncertain": 0,
            "date_range": "No data"
        }
    
    if len(df) == 0:
        return {
            "total_entries": 0,
            "phishing_confirmed": 0,
            "safe_confirmed": 0,
            "uncertain": 0,
            "date_range": "No data"
        }
    
    return {
        "total_entries": len(df),
        "phishing_confirmed": len(df[df['user_verdict'] == 'phishing']) if 'user_verdict' in df.columns else 0,
        "safe_confirmed": len(df[df['user_verdict'] == 'safe']) if 'user_verdict' in df.columns else 0,
        "uncertain": len(df[df['user_verdict'] == 'uncertain']) if 'user_verdict' in df.columns else 0,
        "date_range": f"{df['timestamp'].min()} to {df['timestamp'].max()}" if len(df) > 0 else "No data"
    }


def archive_feedback():
    """
    Archive old feedback data after retraining.
    """
    if not os.path.exists(FEEDBACK_FILE) or os.path.getsize(FEEDBACK_FILE) == 0:
        return
    
    try:
        df = pd.read_csv(FEEDBACK_FILE)
    except pd.errors.EmptyDataError:
        return
    
    if len(df) == 0:
        return
    
    # Append to existing archive
    if os.path.exists(FEEDBACK_ARCHIVE) and os.path.getsize(FEEDBACK_ARCHIVE) > 0:
        try:
            archive_df = pd.read_csv(FEEDBACK_ARCHIVE)
            df = pd.concat([archive_df, df], ignore_index=True)
        except pd.errors.EmptyDataError:
            pass
    
    df.to_csv(FEEDBACK_ARCHIVE, index=False)
    
    # Clear current feedback file
    empty_df = pd.DataFrame(columns=df.columns)
    empty_df.to_csv(FEEDBACK_FILE, index=False)
    
    print(f"Archived {len(df)} feedback entries")


if __name__ == "__main__":
    # For testing
    print("Feedback Collector Module")
    print(f"Feedback file: {FEEDBACK_FILE}")
    print(f"Archive file: {FEEDBACK_ARCHIVE}")