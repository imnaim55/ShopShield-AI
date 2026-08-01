"""
Feedback Storage Module - ShopShield AI
Developed by Naim Shaikh
"""

import os
import sys
import pandas as pd
from datetime import datetime
from huggingface_hub import HfApi

FEEDBACK_FILE = "data/user_feedback.csv"
ARCHIVE_FILE = "data/feedback_archive.csv"

HF_TOKEN = os.getenv("HF_TOKEN")
HF_DATASET_REPO = "imnaim55/shopshield-feedback"
HF_MODEL_REPO = "imnaim55/shopshield-model"


def debug_print(msg):
    print(msg)
    sys.stdout.flush()


def upload_feedback_to_hub(df):
    try:
        csv_data = df.to_csv(index=False)
        api = HfApi()
        api.upload_file(
            path_or_fileobj=csv_data.encode('utf-8'),
            path_in_repo="feedback.csv",
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            token=HF_TOKEN
        )
        debug_print(f"Feedback uploaded to {HF_DATASET_REPO}")
        return True
    except Exception as e:
        debug_print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return False


def save_feedback(url, risk, verdict, comment=""):
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
        debug_print(f"Feedback saved locally: {url}")

        if HF_TOKEN:
            debug_print("Uploading feedback to Hugging Face...")
            success = upload_feedback_to_hub(df)
            debug_print(f"Upload result: {'SUCCESS' if success else 'FAILED'}")
        else:
            debug_print("HF_TOKEN not set. Feedback not uploaded.")

        return True
    except Exception as e:
        debug_print(f"Error saving feedback: {e}")
        return False


def get_feedback():
    try:
        if os.path.exists(FEEDBACK_FILE) and os.path.getsize(FEEDBACK_FILE) > 0:
            return pd.read_csv(FEEDBACK_FILE)
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
    except:
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])


def get_feedback_count():
    try:
        return len(get_feedback())
    except:
        return 0


def get_archive_feedback():
    try:
        if os.path.exists(ARCHIVE_FILE) and os.path.getsize(ARCHIVE_FILE) > 0:
            return pd.read_csv(ARCHIVE_FILE)
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
    except:
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])


def archive_feedback():
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
    if not HF_TOKEN or not os.path.exists(model_path):
        return False
    try:
        api = HfApi()
        api.upload_file(
            path_or_fileobj=model_path,
            path_in_repo="url_phishing_model.pkl",
            repo_id=HF_MODEL_REPO,
            repo_type="model",
            token=HF_TOKEN
        )
        debug_print(f"Model uploaded to {HF_MODEL_REPO}")
        return True
    except Exception as e:
        debug_print(f"Model upload error: {e}")
        return False