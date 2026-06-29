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
import warnings
warnings.filterwarnings('ignore')

from url_analyzer import extract_features_from_url

# Constants
FEEDBACK_FILE = "data/user_feedback.csv"
MODEL_PATH = "models/url_phishing_model.pkl"
ORIGINAL_DATASET = "data/phishing_features.csv"
FEATURE_COLUMNS = [
    "url_length", "num_dots", "has_https", "has_ip",
    "num_subdirs", "num_params", "suspicious_words",
    "special_char_count", "digits_count"
]


def auto_retrain(min_samples=5, force=False):
    """
    Automatically retrain model with new feedback data.
    
    Args:
        min_samples: Minimum number of new samples required for retraining
        force: Force retraining even if samples < min_samples
    
    Returns:
        bool: True if retraining successful, False otherwise
    """
    print("=" * 60)
    print("Auto-Retraining Started")
    print("=" * 60)
    
    # Validate feedback file
    if not os.path.exists(FEEDBACK_FILE):
        print("No feedback data available for retraining")
        return False
    
    feedback_df = pd.read_csv(FEEDBACK_FILE)
    
    if len(feedback_df) == 0:
        print("Feedback file is empty")
        return False
    
    # Identify verdict column
    verdict_column = None
    if 'verdict' in feedback_df.columns:
        verdict_column = 'verdict'
    elif 'user_verdict' in feedback_df.columns:
        verdict_column = 'user_verdict'
    else:
        print("No verdict column found in feedback data")
        return False
    
    # Filter clear feedback
    feedback_df = feedback_df[feedback_df[verdict_column].isin(['phishing', 'safe'])]
    
    if len(feedback_df) < min_samples and not force:
        print(f"Only {len(feedback_df)} samples, need at least {min_samples} for retraining")
        return False
    
    print(f"Found {len(feedback_df)} feedback entries for training")
    
    # Prepare training data
    all_features = []
    all_labels = []
    
    # Load original training data
    if os.path.exists(ORIGINAL_DATASET):
        try:
            original_df = pd.read_csv(ORIGINAL_DATASET)
            
            if all(col in original_df.columns for col in FEATURE_COLUMNS):
                X_orig = original_df[FEATURE_COLUMNS]
                y_orig = original_df['label'].astype(int)
                
                all_features.extend(X_orig.values.tolist())
                all_labels.extend(y_orig.values.tolist())
                
                print(f"Loaded {len(X_orig)} original training samples")
        except Exception as e:
            print(f"Could not load original dataset: {e}")
    
    # Process feedback data
    for _, row in feedback_df.iterrows():
        try:
            features, _ = extract_features_from_url(row['url'])
            feature_values = features.iloc[0].values.tolist()
            label = 1 if row[verdict_column] == 'phishing' else 0
            
            all_features.append(feature_values)
            all_labels.append(label)
        except Exception as e:
            print(f"Could not process URL: {row['url']} - {e}")
            continue
    
    if len(all_features) < 10:
        print("Not enough valid training data")
        return False
    
    # Convert to numpy arrays
    X = np.array(all_features)
    y = np.array(all_labels)
    
    print(f"Total training samples: {len(X)}")
    print(f"Phishing samples: {sum(y)}")
    print(f"Safe samples: {len(y) - sum(y)}")
    
    # Split for validation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    print("Training Random Forest model...")
    
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
    
    # Evaluate model
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    print("\nModel Performance:")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    
    # Save model
    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\nModel saved to {MODEL_PATH}")
    
    # Archive feedback
    archive_feedback(feedback_df)
    
    print("=" * 60)
    print("Auto-Retraining Completed Successfully")
    print("=" * 60)
    
    return True


def archive_feedback(feedback_df):
    """Archive feedback data after retraining."""
    archive_file = "data/feedback_archive.csv"
    
    # Append to existing archive if available
    if os.path.exists(archive_file) and os.path.getsize(archive_file) > 0:
        try:
            archive_df = pd.read_csv(archive_file)
            feedback_df = pd.concat([archive_df, feedback_df], ignore_index=True)
        except pd.errors.EmptyDataError:
            pass
    
    feedback_df.to_csv(archive_file, index=False)
    
    # Clear current feedback file
    empty_df = pd.DataFrame(columns=feedback_df.columns)
    empty_df.to_csv(FEEDBACK_FILE, index=False)
    
    print(f"Archived {len(feedback_df)} feedback entries")
    print("Cleared current feedback file")


if __name__ == "__main__":
    # For manual testing
    auto_retrain(min_samples=1, force=True)