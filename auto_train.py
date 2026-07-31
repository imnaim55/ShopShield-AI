"""
Auto-Retraining Module - ShopShield AI
Developed by Naim Shaikh
"""

print("🔧 auto_train.py loaded")

import pandas as pd
import pickle
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from huggingface_hub import hf_hub_download
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from url_analyzer import extract_features_from_url

FEEDBACK_FILE = "data/user_feedback.csv"
MODEL_PATH = "models/url_phishing_model.pkl"
ORIGINAL_DATASET = "data/phishing_features.csv"
HF_DATASET_REPO = "imnaim55/shopshield-data"
HF_DATASET_FILE = "phishing_features.csv"
STATUS_FILE = "data/retrain_status.txt"
FEATURE_COLUMNS = [
    "url_length", "num_dots", "has_https", "has_ip",
    "num_subdirs", "num_params", "suspicious_words",
    "special_char_count", "digits_count"
]

def write_status(msg):
    with open(STATUS_FILE, "w") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")

def read_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return f.read()
    return "No retrain attempt yet."


def load_or_download_dataset():
    if os.path.exists(ORIGINAL_DATASET):
        write_status(f"✅ Found local dataset: {ORIGINAL_DATASET}")
        return pd.read_csv(ORIGINAL_DATASET)
    try:
        write_status("📥 Downloading dataset from Hugging Face Hub...")
        dataset_path = hf_hub_download(
            repo_id=HF_DATASET_REPO,
            filename=HF_DATASET_FILE,
            repo_type="dataset"
        )
        write_status(f"✅ Downloaded to {dataset_path}")
        return pd.read_csv(dataset_path)
    except Exception as e:
        write_status(f"❌ Could not download dataset: {e}")
        return None


def auto_retrain(min_samples=5, force=False):
    write_status("🔄 Starting retraining...")
    
    if not os.path.exists(FEEDBACK_FILE):
        write_status("❌ No feedback file.")
        return False
    feedback_df = pd.read_csv(FEEDBACK_FILE)
    if feedback_df.empty:
        write_status("❌ Feedback file is empty.")
        return False
    write_status(f"📊 Feedback entries: {len(feedback_df)}")

    verdict_col = 'verdict' if 'verdict' in feedback_df.columns else 'user_verdict'
    if verdict_col not in feedback_df.columns:
        write_status(f"❌ No verdict column found. Available: {feedback_df.columns.tolist()}")
        return False

    feedback_df = feedback_df[feedback_df[verdict_col].isin(['phishing', 'safe'])]
    write_status(f"📊 Clear feedback entries: {len(feedback_df)}")
    if len(feedback_df) < min_samples and not force:
        write_status(f"⏳ Need {min_samples} feedback samples, have {len(feedback_df)}.")
        return False

    all_features = []
    all_labels = []

    original_df = load_or_download_dataset()
    if original_df is not None:
        if all(col in original_df.columns for col in FEATURE_COLUMNS):
            X_orig = original_df[FEATURE_COLUMNS]
            y_orig = original_df['label'].astype(int)
            all_features.extend(X_orig.values.tolist())
            all_labels.extend(y_orig.values.tolist())
            write_status(f"📚 Loaded {len(X_orig)} original training samples.")
        else:
            write_status("⚠️ Original dataset missing required columns.")
    else:
        write_status("⚠️ Original dataset not available. Training only with feedback data.")

    processed = 0
    for _, row in feedback_df.iterrows():
        try:
            features, _ = extract_features_from_url(row['url'])
            feature_values = features.iloc[0].values.tolist()
            label = 1 if row[verdict_col] == 'phishing' else 0
            all_features.append(feature_values)
            all_labels.append(label)
            processed += 1
        except Exception as e:
            write_status(f"⚠️ Could not process URL: {row['url']} - {e}")
            continue
    write_status(f"📝 Processed {processed} feedback entries.")

    if len(all_features) < 10:
        write_status(f"❌ Not enough total training samples: {len(all_features)} (need ≥10).")
        return False

    X = np.array(all_features)
    y = np.array(all_labels)
    write_status(f"📊 Total training samples: {len(X)} (Phishing: {sum(y)}, Safe: {len(y)-sum(y)})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    write_status(f"📈 Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    write_status(f"📈 Precision: {precision_score(y_test, y_pred):.4f}")
    write_status(f"📈 Recall: {recall_score(y_test, y_pred):.4f}")
    write_status(f"📈 F1 Score: {f1_score(y_test, y_pred):.4f}")

    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    write_status(f"✅ Model saved to {MODEL_PATH}")

    archive_file = "data/feedback_archive.csv"
    if os.path.exists(archive_file) and os.path.getsize(archive_file) > 0:
        try:
            archive_df = pd.read_csv(archive_file)
            feedback_df = pd.concat([archive_df, feedback_df], ignore_index=True)
        except:
            pass
    feedback_df.to_csv(archive_file, index=False)
    pd.DataFrame(columns=feedback_df.columns).to_csv(FEEDBACK_FILE, index=False)
    write_status("✅ Feedback archived.")
    write_status("✅ Auto-retraining completed successfully.")
    return True


if __name__ == "__main__":
    auto_retrain(min_samples=1, force=True)