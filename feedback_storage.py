"""
Feedback Storage Module - ShopShield AI (Pure Virtual)
Developed by Naim Shaikh
"""

import os
import sys
import pandas as pd
from datetime import datetime
from huggingface_hub import HfApi
import requests
from io import StringIO

HF_TOKEN = os.getenv("HF_TOKEN")
HF_FEEDBACK_REPO = "imnaim55/shopshield-feedback"
HF_DATA_REPO = "imnaim55/shopshield-data"
HF_MODEL_REPO = "imnaim55/shopshield-model"


def debug_print(msg):
    print(msg)
    sys.stdout.flush()


def read_csv_from_hub(filename):
    """Read CSV directly from Hugging Face Hub."""
    try:
        url = f"https://huggingface.co/datasets/{HF_FEEDBACK_REPO}/resolve/main/{filename}"
        response = requests.get(url)
        if response.status_code == 200:
            return pd.read_csv(StringIO(response.text))
        return pd.DataFrame()
    except Exception as e:
        debug_print(f"Error reading {filename}: {e}")
        return pd.DataFrame()


def write_csv_to_hub(df, filename):
    """Write CSV directly to Hugging Face Hub."""
    try:
        csv_data = df.to_csv(index=False)
        api = HfApi()
        api.upload_file(
            path_or_fileobj=csv_data.encode('utf-8'),
            path_in_repo=filename,
            repo_id=HF_FEEDBACK_REPO,
            repo_type="dataset",
            token=HF_TOKEN
        )
        debug_print(f"Uploaded {filename} to Hugging Face")
        return True
    except Exception as e:
        debug_print(f"Error uploading {filename}: {e}")
        return False


def save_feedback(url, risk, verdict, comment=""):
    """Save feedback directly to Hugging Face."""
    try:
        feedback_entry = {
            "url": url,
            "risk_score": risk,
            "verdict": verdict,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }

        df = read_csv_from_hub("feedback.csv")
        new_df = pd.DataFrame([feedback_entry])
        
        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)
        
        success = write_csv_to_hub(df, "feedback.csv")
        debug_print(f"Feedback saved: {url} -> {verdict}")
        return success
        
    except Exception as e:
        debug_print(f"Error saving feedback: {e}")
        return False


def get_feedback():
    """Get all feedback from Hugging Face."""
    try:
        return read_csv_from_hub("feedback.csv")
    except:
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])


def get_feedback_count():
    """Get number of feedback entries."""
    try:
        df = get_feedback()
        return len(df)
    except:
        return 0


def archive_feedback():
    """Archive feedback on Hugging Face."""
    try:
        df = read_csv_from_hub("feedback.csv")
        if df.empty:
            return False
        
        archive_df = read_csv_from_hub("feedback_archive.csv")
        if archive_df.empty:
            archive_df = df
        else:
            archive_df = pd.concat([archive_df, df], ignore_index=True)
        
        write_csv_to_hub(archive_df, "feedback_archive.csv")
        empty_df = pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
        write_csv_to_hub(empty_df, "feedback.csv")
        
        debug_print("Feedback archived")
        return True
    except Exception as e:
        debug_print(f"Archive error: {e}")
        return False


def download_dataset_from_hub():
    """Download phishing_features.csv from Hugging Face."""
    try:
        from huggingface_hub import hf_hub_download
        dataset_path = hf_hub_download(
            repo_id=HF_DATA_REPO,
            filename="phishing_features.csv",
            repo_type="dataset",
            token=HF_TOKEN
        )
        debug_print(f"Dataset downloaded from Hugging Face")
        return pd.read_csv(dataset_path)
    except Exception as e:
        debug_print(f"Dataset download error: {e}")
        return None


def upload_model_to_hub(model_path="models/url_phishing_model.pkl"):
    """Upload trained model to Hugging Face."""
    if not os.path.exists(model_path):
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


def load_model_from_hub():
    """Load model directly from Hugging Face."""
    try:
        from huggingface_hub import hf_hub_download
        import pickle
        model_path = hf_hub_download(
            repo_id=HF_MODEL_REPO,
            filename="url_phishing_model.pkl",
            repo_type="model",
            token=HF_TOKEN
        )
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        debug_print(f"Model loaded from Hugging Face")
        return model
    except Exception as e:
        debug_print(f"Model download error: {e}")
        return None