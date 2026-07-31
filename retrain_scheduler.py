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

FEEDBACK_FILE = "data/user_feedback.csv"
RETRAIN_THRESHOLD = 5
CHECK_INTERVAL_MINUTES = 30


def check_and_retrain():
    if not os.path.exists(FEEDBACK_FILE):
        return
    try:
        df = pd.read_csv(FEEDBACK_FILE)
        if len(df) >= RETRAIN_THRESHOLD:
            print(f"Scheduled Retraining Triggered - {datetime.now()}")
            print(f"Found {len(df)} feedback entries")
            if auto_retrain(min_samples=RETRAIN_THRESHOLD):
                print("Auto-retraining completed successfully")
            else:
                print("Auto-retraining failed or was skipped")
        else:
            print(f"Only {len(df)} entries, need {RETRAIN_THRESHOLD} for retraining")
    except Exception as e:
        print(f"Error checking feedback: {e}")


def run_scheduler():
    print("Starting Retraining Scheduler...")
    print(f"Checking every {CHECK_INTERVAL_MINUTES} minutes. Press Ctrl+C to stop.")
    check_and_retrain()
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_and_retrain)
    schedule.every().day.at("00:00").do(check_and_retrain)
    schedule.every(6).hours.do(check_and_retrain)
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            print("\nScheduler stopped")
            break
        except Exception as e:
            print(f"Scheduler error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    run_scheduler()