"""
Feedback Storage Module - ShopShield AI
Developed by Naim Shaikh
"""

import os
import sys
import pandas as pd
from datetime import datetime
import requests

FEEDBACK_FILE = "data/user_feedback.csv"
ARCHIVE_FILE = "data/feedback_archive.csv"

# Hugging Face Config
HF_TOKEN = os.getenv("HF_TOKEN")
HF_DATASET_REPO = "imnaim55/shopshield-feedback"
HF_MODEL_REPO = "imnaim55/shopshield-model"

def debug_print(msg):
    print(msg)
    sys.stdout.flush()


def save_feedback(url, risk, verdict, comment=""):
    """Save user feedback locally and upload to Hugging Face."""
    try:
        os.makedirs("data", exist_ok=True)
        
        feedback_entry = {
            "url": url,
            "risk_score": risk,
            "verdict": verdict,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save locally
        if os.path.exists(FEEDBACK_FILE) and os.path.getsize(FEEDBACK_FILE) > 0:
            try:
                df = pd.read_csv(FEEDBACK_FILE)
            except:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
        
        df = pd.concat([df, pd.DataFrame([feedback_entry])], ignore_index=True)
        df.to_csv(FEEDBACK_FILE, index=False)
        debug_print(f"✅ Feedback saved locally: {url}")
        
        # Upload to Hugging Face
        if HF_TOKEN:
            debug_print("📤 Uploading feedback to Hugging Face...")
            success = upload_feedback_to_hub(df)
            debug_print(f"   Upload result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        else:
            debug_print("❌ HF_TOKEN not set! Feedback not uploaded.")
        
        return True
    except Exception as e:
        debug_print(f"❌ Error saving feedback: {e}")
        return False


def upload_feedback_to_hub(df):
    """Upload feedback CSV to Hugging Face Hub."""
    try:
        # Convert DataFrame to CSV
        csv_data = df.to_csv(index=False)
        
        # Upload using Hugging Face API
        url = f"https://huggingface.co/api/datasets/{HF_DATASET_REPO}/upload/main/feedback.csv"
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/octet-stream"
        }
        
        response = requests.put(url, headers=headers, data=csv_data.encode('utf-8'))
        
        if response.status_code == 200 or response.status_code == 201:
            debug_print(f"✅ Feedback uploaded to {HF_DATASET_REPO}")
            return True
        else:
            debug_print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        debug_print(f"❌ Upload error: {e}")
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


def upload_model_to_hub(model_path="models/url_phishing_model.pkl"):
    """Upload trained model to Hugging Face Hub."""
    if not HF_TOKEN or not os.path.exists(model_path):
        return False
    try:
        with open(model_path, 'rb') as f:
            model_data = f.read()
        
        url = f"https://huggingface.co/api/models/{HF_MODEL_REPO}/upload/main/url_phishing_model.pkl"
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/octet-stream"
        }
        
        response = requests.put(url, headers=headers, data=model_data)
        
        if response.status_code == 200 or response.status_code == 201:
            debug_print(f"✅ Model uploaded to {HF_MODEL_REPO}")
            return True
        else:
            debug_print(f"❌ Model upload failed: {response.status_code}")
            return False
    except Exception as e:
        debug_print(f"❌ Model upload error: {e}")
        return False