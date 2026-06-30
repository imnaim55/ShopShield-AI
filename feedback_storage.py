"""
Feedback Storage Module - ShopShield AI
Developed by Naim Shaikh
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import streamlit as st
import os

SHEET_NAME = "ShopShield Feedback"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_credentials():
    """Get credentials from local file or Streamlit secrets."""
    try:
        # Check if running on Streamlit Cloud
        is_cloud = os.getenv("STREAMLIT_CLOUD") or os.getenv("STREAMLIT_SHARING")
        
        # Local development - use credentials.json
        if not is_cloud and os.path.exists("credentials.json"):
            print("✅ Using local credentials.json")
            return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
        
        # Deployed app - use Streamlit secrets
        try:
            if "google_credentials" in st.secrets:
                print("✅ Using Streamlit Secrets")
                creds_dict = dict(st.secrets["google_credentials"])
                return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        except Exception as e:
            print(f"❌ Error reading secrets: {e}")
        
        print("❌ No credentials found!")
        return None
        
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None

def get_sheet():
    """Get Google Sheet."""
    try:
        creds = get_credentials()
        if creds is None:
            return None
        
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def save_feedback_sheet(url, risk, verdict, comment=""):
    """Save feedback to Google Sheets."""
    try:
        sheet = get_sheet()
        if sheet is None:
            return False
        
        row = [url, risk, verdict, comment, datetime.now().isoformat()]
        sheet.append_row(row)
        return True
        
    except Exception as e:
        print(f"❌ Error saving: {e}")
        return False

def get_feedback_sheet():
    """Get all feedback from Google Sheets."""
    try:
        sheet = get_sheet()
        if sheet is None:
            return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
        
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
        
    except Exception as e:
        print(f"❌ Error reading: {e}")
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])

def get_feedback_count_sheet():
    """Get number of feedback entries."""
    try:
        df = get_feedback_sheet()
        return len(df)
    except:
        return 0