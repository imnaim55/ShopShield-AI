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
import json

SHEET_NAME = "ShopShield Feedback"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_credentials():
    """Get credentials from Streamlit Secrets (deployed) or local file (development)."""
    try:
        # Check if running on Streamlit Cloud
        if os.getenv("STREAMLIT_CLOUD") or os.getenv("STREAMLIT_SHARING"):
            print("Running on Streamlit Cloud - checking secrets...")
            
            # Try to get credentials from secrets
            if "google_credentials" in st.secrets:
                print("✅ Found google_credentials in secrets")
                creds_dict = dict(st.secrets["google_credentials"])
                return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
            elif "google_credentials_raw" in st.secrets:
                print("✅ Found google_credentials_raw in secrets")
                creds_dict = json.loads(st.secrets["google_credentials_raw"])
                return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
            else:
                print("❌ No Google credentials found in secrets!")
                print(f"Available secrets: {list(st.secrets.keys())}")
                return None
        else:
            # Local development - use credentials.json
            if os.path.exists("credentials.json"):
                print("✅ Using local credentials.json")
                return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
            else:
                print("❌ credentials.json not found!")
                return None
                
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None

def get_sheet():
    """Get the Google Sheet."""
    try:
        creds = get_credentials()
        if creds is None:
            return None
        
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        print(f"✅ Connected to sheet: {SHEET_NAME}")
        return sheet
    except Exception as e:
        print(f"❌ Error connecting to sheet: {e}")
        return None

def save_feedback_sheet(url, risk, verdict, comment=""):
    """Save feedback to Google Sheets."""
    try:
        sheet = get_sheet()
        if sheet is None:
            return False
        
        row = [url, risk, verdict, comment, datetime.now().isoformat()]
        sheet.append_row(row)
        print(f"✅ Saved: {url} -> {verdict}")
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
    except Exception as e:
        print(f"❌ Error getting count: {e}")
        return 0