"""
Auto-Retraining Module - ShopShield AI
Developed by Naim Shaikh
"""

import os  # <-- ADD THIS LINE
import pandas as pd
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from feedback_storage import get_feedback, archive_feedback
from url_analyzer import extract_features_from_url
import requests
import warnings
warnings.filterwarnings('ignore')

# Hugging Face Config
HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL_REPO = "imnaim55/shopshield-model"

MODEL_PATH = "models/url_phishing_model.pkl"
ORIGINAL_DATASET = "data/phishing_features.csv"
FEATURE_COLUMNS = [
    "url_length", "num_dots", "has_https", "has_ip",
    "num_subdirs", "num_params", "suspicious_words",
    "special_char_count", "digits_count"
]


def upload_model_to_hub():
    """Upload trained model to Hugging Face Hub."""
    if not HF_TOKEN or not os.path.exists(MODEL_PATH):
        return False
    try:
        url = f"https://huggingface.co/api/models/{HF_MODEL_REPO}/upload/main/model.pkl"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        files = {'file': ('model.pkl', open(MODEL_PATH, 'rb'), 'application/octet-stream')}
        response = requests.post(url, headers=headers, files=files)
        return response.status_code == 200
    except Exception as e:
        print(f"Error uploading model: {e}")
        return False


def auto_retrain(min_samples=1, force=True):
    """Retrain model with feedback data."""
    print("Starting retraining...")
    
    feedback_df = get_feedback()
    if feedback_df.empty:
        print("No feedback data.")
        return False
    
    verdict_col = 'verdict' if 'verdict' in feedback_df.columns else 'user_verdict'
    if verdict_col not in feedback_df.columns:
        print("No verdict column.")
        return False
    
    feedback_df = feedback_df[feedback_df[verdict_col].isin(['phishing', 'safe'])]
    if len(feedback_df) < min_samples and not force:
        print(f"Need {min_samples} feedback samples, have {len(feedback_df)}.")
        return False
    
    print(f"Feedback entries: {len(feedback_df)}")
    
    all_features = []
    all_labels = []
    
    # Load original dataset
    if os.path.exists(ORIGINAL_DATASET):
        try:
            original_df = pd.read_csv(ORIGINAL_DATASET)
            if all(col in original_df.columns for col in FEATURE_COLUMNS):
                X_orig = original_df[FEATURE_COLUMNS]
                y_orig = original_df['label'].astype(int)
                all_features.extend(X_orig.values.tolist())
                all_labels.extend(y_orig.values.tolist())
                print(f"Loaded {len(X_orig)} original samples.")
        except Exception as e:
            print(f"Error loading dataset: {e}")
    
    # Process feedback
    for _, row in feedback_df.iterrows():
        try:
            features, _ = extract_features_from_url(row['url'])
            feature_values = features.iloc[0].values.tolist()
            label = 1 if row[verdict_col] == 'phishing' else 0
            all_features.append(feature_values)
            all_labels.append(label)
        except:
            continue
    
    if len(all_features) < 10:
        print(f"Not enough training samples: {len(all_features)}")
        return False
    
    X = np.array(all_features)
    y = np.array(all_labels)
    print(f"Total samples: {len(X)}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred):.4f}")
    print(f"F1 Score: {f1_score(y_test, y_pred):.4f}")
    
    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    # Upload model to Hugging Face
    if HF_TOKEN:
        upload_model_to_hub()
    
    archive_feedback()
    print("Retraining completed successfully.")
    return True


if __name__ == "__main__":
    auto_retrain(min_samples=1, force=True)