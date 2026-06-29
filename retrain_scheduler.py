"""
Retraining Scheduler Module - ShopShield AI
Developed by Naim Shaikh
"""

import schedule
import time
import os
import pandas as pd
from datetime import datetime
from auto_train import auto_retrain

# Constants
FEEDBACK_FILE = "data/user_feedback.csv"
RETRAIN_THRESHOLD = 5
CHECK_INTERVAL_MINUTES = 30


def check_and_retrain():
    """Check if enough feedback exists and trigger retraining."""
    if not os.path.exists(FEEDBACK_FILE):
        return
    
    try:
        df = pd.read_csv(FEEDBACK_FILE)
        
        if len(df) >= RETRAIN_THRESHOLD:
            print("\n" + "=" * 60)
            print(f"Scheduled Retraining Triggered - {datetime.now()}")
            print(f"Found {len(df)} feedback entries")
            print("=" * 60)
            
            success = auto_retrain(min_samples=RETRAIN_THRESHOLD)
            
            if success:
                print("Auto-retraining completed successfully")
            else:
                print("Auto-retraining failed or was skipped")
        else:
            print(f"Only {len(df)} feedback entries, need {RETRAIN_THRESHOLD} for retraining")
    
    except Exception as e:
        print(f"Error checking feedback: {e}")


def run_scheduler():
    """Run the retraining scheduler."""
    print("Starting Retraining Scheduler...")
    print(f"Checking for new feedback every {CHECK_INTERVAL_MINUTES} minutes")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Run once immediately
    check_and_retrain()
    
    # Schedule regular checks
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_and_retrain)
    schedule.every().day.at("00:00").do(check_and_retrain)  # Daily backup
    schedule.every(6).hours.do(check_and_retrain)  # Every 6 hours backup
    
    print(f"Scheduler is running. Monitoring {FEEDBACK_FILE}...")
    print("=" * 60)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nScheduler stopped by user")
            break
        except Exception as e:
            print(f"Scheduler error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    run_scheduler()