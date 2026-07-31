"""
Auto-Retraining Module - ShopShield AI
Developed by Naim Shaikh
"""

import pandas as pd
import pickle
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from huggingface_hub import hf_hub_download
import warnings
warnings.filterwarnings('ignore')

from url_analyzer import extract_features_from_url

FEEDBACK_FILE = "data/user_feedback.csv"
MODEL_PATH = "models/url_phishing_model.pkl"
ORIGINAL_DATASET = "data/phishing_features.csv"
HF_DATASET_REPO = "imnaim55/shopshield-data"
HF_DATASET_FILE = "phishing_features.csv"
FEATURE_COLUMNS = [
    "url_length", "num_dots", "has_https", "has_ip",
    "num_subdirs", "num_params", "suspicious_words",
    "special_char_count", "digits_count"
]


def load_or_download_dataset():
    """Load dataset locally; if missing, download from Hugging Face Hub."""
    if os.path.exists(ORIGINAL_DATASET):
        print(f"✅ Found local dataset: {ORIGINAL_DATASET}")
        return pd.read_csv(ORIGINAL_DATASET)
    try:
        print("📥 Downloading dataset from Hugging Face Hub...")
        dataset_path = hf_hub_download(
            repo_id=HF_DATASET_REPO,
            filename=HF_DATASET_FILE,
            repo_type="dataset"
        )
        print(f"✅ Downloaded to {dataset_path}")
        return pd.read_csv(dataset_path)
    except Exception as e:
        print(f"❌ Could not download dataset: {e}")
        return None


def auto_retrain(min_samples=5, force=False):
    print("🔄 Starting retraining...")

    # 1. Check feedback file
    if not os.path.exists(FEEDBACK_FILE):
        print("❌ No feedback file.")
        return False
    feedback_df = pd.read_csv(FEEDBACK_FILE)
    if feedback_df.empty:
        print("❌ Feedback file is empty.")
        return False
    print(f"📊 Feedback entries: {len(feedback_df)}")

    # 2. Identify verdict column
    verdict_col = 'verdict' if 'verdict' in feedback_df.columns else 'user_verdict'
    if verdict_col not in feedback_df.columns:
        print(f"❌ No verdict column found. Available: {feedback_df.columns.tolist()}")
        return False

    # 3. Filter clear feedback
    feedback_df = feedback_df[feedback_df[verdict_col].isin(['phishing', 'safe'])]
    print(f"📊 Clear feedback entries: {len(feedback_df)}")
    if len(feedback_df) < min_samples and not force:
        print(f"⏳ Need {min_samples} feedback samples, have {len(feedback_df)}.")
        return False

    all_features = []
    all_labels = []

    # 4. Load original dataset
    original_df = load_or_download_dataset()
    if original_df is not None:
        if all(col in original_df.columns for col in FEATURE_COLUMNS):
            X_orig = original_df[FEATURE_COLUMNS]
            y_orig = original_df['label'].astype(int)
            all_features.extend(X_orig.values.tolist())
            all_labels.extend(y_orig.values.tolist())
            print(f"📚 Loaded {len(X_orig)} original training samples.")
        else:
            print("⚠️ Original dataset missing required columns.")
            print(f"   Expected: {FEATURE_COLUMNS}")
            print(f"   Found: {original_df.columns.tolist()}")
            # Continue anyway, use only feedback
    else:
        print("⚠️ Original dataset not available. Training only with feedback data.")

    # 5. Process feedback
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
            print(f"⚠️ Could not process URL: {row['url']} - {e}")
            continue
    print(f"📝 Processed {processed} feedback entries.")

    if len(all_features) < 10:
        print(f"❌ Not enough total training samples: {len(all_features)} (need ≥10).")
        return False

    X = np.array(all_features)
    y = np.array(all_labels)

    print(f"📊 Total training samples: {len(X)}")
    print(f"   Phishing: {sum(y)}")
    print(f"   Safe: {len(y)-sum(y)}")

    # 6. Train
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

    # 7. Evaluate
    y_pred = model.predict(X_test)
    print(f"📈 Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"📈 Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"📈 Recall:    {recall_score(y_test, y_pred):.4f}")
    print(f"📈 F1 Score:  {f1_score(y_test, y_pred):.4f}")

    # 8. Save model
    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    print(f"✅ Model saved to {MODEL_PATH}")

    # 9. Archive feedback
    archive_file = "data/feedback_archive.csv"
    if os.path.exists(archive_file) and os.path.getsize(archive_file) > 0:
        try:
            archive_df = pd.read_csv(archive_file)
            feedback_df = pd.concat([archive_df, feedback_df], ignore_index=True)
        except:
            pass
    feedback_df.to_csv(archive_file, index=False)
    pd.DataFrame(columns=feedback_df.columns).to_csv(FEEDBACK_FILE, index=False)
    print("✅ Feedback archived.")

    return True