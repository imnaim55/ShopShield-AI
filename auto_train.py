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

# Force print to be visible in logs
def debug_print(msg):
    print(msg)
    sys.stdout.flush()


def auto_retrain(min_samples=1, force=True):
    """Retrain model with feedback data."""
    debug_print("=" * 60)
    debug_print("🚀 AUTO-RETRAINING STARTED")
    debug_print("=" * 60)
    
    try:
        # 1. Get feedback
        debug_print("📊 Getting feedback data...")
        feedback_df = get_feedback()
        debug_print(f"   Raw feedback entries: {len(feedback_df)}")
        
        if feedback_df.empty:
            debug_print("❌ No feedback data found!")
            return False
        
        # 2. Check columns
        debug_print(f"📋 Columns: {feedback_df.columns.tolist()}")
        
        # 3. Find verdict column
        verdict_col = None
        for col in ['verdict', 'user_verdict']:
            if col in feedback_df.columns:
                verdict_col = col
                break
        
        if verdict_col is None:
            debug_print("❌ No verdict column found!")
            return False
        
        debug_print(f"✅ Using verdict column: '{verdict_col}'")
        
        # 4. Filter clear feedback
        feedback_df = feedback_df[feedback_df[verdict_col].isin(['phishing', 'safe'])]
        debug_print(f"📊 Clear feedback entries: {len(feedback_df)}")
        
        if len(feedback_df) < min_samples and not force:
            debug_print(f"⏳ Need {min_samples}, have {len(feedback_df)}")
            return False
        
        # 5. Prepare training data
        all_features = []
        all_labels = []
        
        # Load original dataset if exists and has enough data
        if os.path.exists(ORIGINAL_DATASET):
            try:
                original_df = pd.read_csv(ORIGINAL_DATASET)
                debug_print(f"📚 Loaded original dataset: {len(original_df)} rows")
                
                if all(col in original_df.columns for col in FEATURE_COLUMNS):
                    X_orig = original_df[FEATURE_COLUMNS]
                    y_orig = original_df['label'].astype(int)
                    all_features.extend(X_orig.values.tolist())
                    all_labels.extend(y_orig.values.tolist())
                    debug_print(f"   ✅ Added {len(X_orig)} original samples")
                else:
                    debug_print("   ⚠️ Missing columns in original dataset, using only feedback")
            except Exception as e:
                debug_print(f"   ⚠️ Error loading dataset: {e}")
        else:
            debug_print(f"⚠️ Original dataset not found: {ORIGINAL_DATASET}")
            debug_print("   Using only feedback data for training")
        
        # Process feedback
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
                debug_print(f"⚠️ Failed: {row['url'][:30]} - {e}")
        
        debug_print(f"📊 Processed {processed} feedback URLs")
        
        # CHANGE: Reduced from 10 to 5
        if len(all_features) < 5:
            debug_print(f"❌ Not enough samples: {len(all_features)} (need at least 5)")
            return False
        
        X = np.array(all_features)
        y = np.array(all_labels)
        debug_print(f"📊 Total samples: {len(X)}")
        
        # 6. Train model
        debug_print("🔄 Training Random Forest model...")
        
        # If only 5 samples, use all for training (no test split)
        if len(X) < 10:
            model = RandomForestClassifier(
                n_estimators=50,
                max_depth=8,
                min_samples_split=3,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            )
            model.fit(X, y)
            debug_print("   ⚠️ Small dataset: used all samples for training")
        else:
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
            
            # Evaluate
            y_pred = model.predict(X_test)
            debug_print(f"📈 Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        
        # 7. Save model
        os.makedirs("models", exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        debug_print(f"✅ Model saved to {MODEL_PATH}")
        
        # Upload model to Hugging Face
        if HF_TOKEN:
            debug_print("📤 Uploading model to Hugging Face...")
            success = upload_model_to_hub()
            debug_print(f"   Upload result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        else:
            debug_print("❌ HF_TOKEN not set! Model not uploaded.")
        
        # 8. Archive feedback
        archive_feedback()
        debug_print("✅ Feedback archived")
        
        debug_print("=" * 60)
        debug_print("✅ RETRAINING COMPLETED SUCCESSFULLY!")
        debug_print("=" * 60)
        return True
        
    except Exception as e:
        debug_print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # For testing
    auto_retrain(min_samples=1, force=True)