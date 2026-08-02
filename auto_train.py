"""
Auto-Retraining Module - ShopShield AI
Developed by Naim Shaikh
"""

import os
import sys
import pandas as pd
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from feedback_storage import get_feedback, archive_feedback, download_dataset_from_hub, upload_model_to_hub
from url_analyzer import extract_features_from_url
import warnings
warnings.filterwarnings('ignore')

MODEL_PATH = "models/url_phishing_model.pkl"
FEATURE_COLUMNS = [
    "url_length", "num_dots", "has_https", "has_ip",
    "num_subdirs", "num_params", "suspicious_words",
    "special_char_count", "digits_count"
]


def debug_print(msg):
    print(msg)
    sys.stdout.flush()


def auto_retrain(min_samples=1, force=True):
    debug_print("=" * 60)
    debug_print("AUTO-RETRAINING STARTED")
    debug_print("=" * 60)

    try:
        feedback_df = get_feedback()
        debug_print(f"Raw feedback entries: {len(feedback_df)}")

        if feedback_df.empty:
            debug_print("No feedback data found")
            return False

        verdict_col = 'verdict' if 'verdict' in feedback_df.columns else 'user_verdict'
        if verdict_col not in feedback_df.columns:
            debug_print("No verdict column found")
            return False

        debug_print(f"Using verdict column: '{verdict_col}'")

        feedback_df = feedback_df[feedback_df[verdict_col].isin(['phishing', 'safe'])]
        debug_print(f"Clear feedback entries: {len(feedback_df)}")

        if len(feedback_df) < min_samples and not force:
            debug_print(f"Need {min_samples}, have {len(feedback_df)}")
            return False

        all_features = []
        all_labels = []

        dataset_df = download_dataset_from_hub()
        if dataset_df is not None:
            if all(col in dataset_df.columns for col in FEATURE_COLUMNS):
                X_orig = dataset_df[FEATURE_COLUMNS]
                y_orig = dataset_df['label'].astype(int)
                all_features.extend(X_orig.values.tolist())
                all_labels.extend(y_orig.values.tolist())
                debug_print(f"Added {len(X_orig)} samples from dataset")
            else:
                debug_print("Dataset missing required columns")
        else:
            debug_print("Could not download dataset")

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
                debug_print(f"Failed: {row['url'][:30]} - {e}")

        debug_print(f"Processed {processed} feedback URLs")

        if len(all_features) < 5:
            debug_print(f"Not enough samples: {len(all_features)}")
            return False

        X = np.array(all_features)
        y = np.array(all_labels)
        debug_print(f"Total samples: {len(X)}")

        debug_print("Training Random Forest model")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        debug_print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")

        os.makedirs("models", exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        debug_print(f"Model saved locally")

        debug_print("Uploading model to Hugging Face")
        upload_model_to_hub(MODEL_PATH)

        archive_feedback()
        debug_print("Feedback archived on Hugging Face")

        debug_print("=" * 60)
        debug_print("RETRAINING COMPLETED SUCCESSFULLY")
        debug_print("=" * 60)
        return True

    except Exception as e:
        debug_print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    auto_retrain(min_samples=1, force=True)