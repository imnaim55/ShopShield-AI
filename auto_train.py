"""
Auto-Retraining Module - ShopShield AI
Developed by Naim Shaikh
"""
# Hugging Face Config
HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL_REPO = "imnaim55/shopshield-model"

import pandas as pd
import pickle
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from feedback_storage import get_feedback, archive_feedback
from url_analyzer import extract_features_from_url
import warnings
warnings.filterwarnings('ignore')

MODEL_PATH = "models/url_phishing_model.pkl"
ORIGINAL_DATASET = "data/phishing_features.csv"
FEATURE_COLUMNS = [
    "url_length", "num_dots", "has_https", "has_ip",
    "num_subdirs", "num_params", "suspicious_words",
    "special_char_count", "digits_count"
]


def auto_retrain(min_samples=1, force=True):
    """Retrain model with feedback data - COMBINES with existing knowledge."""
    print("=" * 60)
    print("Starting Auto-Retraining...")
    print("=" * 60)
    
    # 1. Get feedback
    feedback_df = get_feedback()
    if feedback_df.empty:
        print("❌ No feedback data available.")
        return False
    
    # 2. Identify verdict column
    verdict_col = 'verdict' if 'verdict' in feedback_df.columns else 'user_verdict'
    if verdict_col not in feedback_df.columns:
        print("❌ No verdict column found.")
        return False
    
    # 3. Filter clear feedback
    feedback_df = feedback_df[feedback_df[verdict_col].isin(['phishing', 'safe'])]
    
    if len(feedback_df) < min_samples and not force:
        print(f"⏳ Need {min_samples} feedback samples, have {len(feedback_df)}.")
        return False
    
    print(f"📊 Found {len(feedback_df)} feedback entries")
    print(f"   Phishing: {len(feedback_df[feedback_df[verdict_col] == 'phishing'])}")
    print(f"   Safe: {len(feedback_df[feedback_df[verdict_col] == 'safe'])}")
    
    # 4. Load existing model if available
    existing_model = None
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, 'rb') as f:
                existing_model = pickle.load(f)
            print(f"📚 Loaded existing model with {existing_model.n_features_in_} features")
        except Exception as e:
            print(f"⚠️ Could not load existing model: {e}")
    
    # 5. Prepare training data
    all_features = []
    all_labels = []
    
    # Add original training data if available
    if os.path.exists(ORIGINAL_DATASET):
        try:
            original_df = pd.read_csv(ORIGINAL_DATASET)
            if all(col in original_df.columns for col in FEATURE_COLUMNS):
                X_orig = original_df[FEATURE_COLUMNS]
                y_orig = original_df['label'].astype(int)
                all_features.extend(X_orig.values.tolist())
                all_labels.extend(y_orig.values.tolist())
                print(f"📚 Added {len(X_orig)} original training samples")
        except Exception as e:
            print(f"⚠️ Could not load original dataset: {e}")
    
    # 6. Process feedback URLs
    processed = 0
    failed = 0
    feedback_features = []
    feedback_labels = []
    
    for _, row in feedback_df.iterrows():
        try:
            features, _ = extract_features_from_url(row['url'])
            feature_values = features.iloc[0].values.tolist()
            label = 1 if row[verdict_col] == 'phishing' else 0
            
            # Validate feature count
            if existing_model and len(feature_values) != existing_model.n_features_in_:
                print(f"⚠️ Feature mismatch: got {len(feature_values)}, expected {existing_model.n_features_in_}")
                continue
            
            feedback_features.append(feature_values)
            feedback_labels.append(label)
            processed += 1
        except Exception as e:
            failed += 1
            continue
    
    print(f"✅ Processed {processed} feedback URLs, {failed} failed")
    
    if len(feedback_features) < 3:
        print(f"❌ Need at least 3 valid feedback entries. Only have {len(feedback_features)}.")
        return False
    
    # 7. Add feedback to training data
    all_features.extend(feedback_features)
    all_labels.extend(feedback_labels)
    
    print(f"📊 Total training samples: {len(all_features)}")
    print(f"   Phishing: {sum(all_labels)}")
    print(f"   Safe: {len(all_labels) - sum(all_labels)}")
    
    if len(all_features) < 10:
        print("❌ Not enough training data")
        return False
    
    X = np.array(all_features)
    y = np.array(all_labels)
    
    # 8. Train new model
    print("\n🔄 Training Random Forest model...")
    
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    model.fit(X, y)
    
    # 9. Evaluate
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, zero_division=0)
    recall = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    
    print(f"\n📈 Model Performance:")
    print(f"   Accuracy: {accuracy*100:.1f}%")
    print(f"   Precision: {precision*100:.1f}%")
    print(f"   Recall: {recall*100:.1f}%")
    print(f"   F1 Score: {f1*100:.1f}%")
    
    # 10. Save model
    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    print(f"\n✅ Model saved to {MODEL_PATH}")
    
    # 11. Archive feedback
    archive_feedback()
    print("✅ Feedback archived")
    
    print("=" * 60)
    print("Auto-Retraining Completed Successfully!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    auto_retrain(min_samples=1, force=True)