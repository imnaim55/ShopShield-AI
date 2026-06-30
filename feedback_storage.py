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
        if os.getenv("STREAMLIT_CLOUD") or os.getenv("STREAMLIT_SHARING"):
            print("🔍 Running on Streamlit Cloud")
            
            # Debug: Show what's in secrets
            print(f"📋 Secrets keys: {list(st.secrets.keys())}")
            
            if "google_credentials_raw" in st.secrets:
                print("✅ Found google_credentials_raw")
                try:
                    creds_dict = json.loads(st.secrets["google_credentials_raw"])
                    print(f"✅ Loaded JSON with keys: {list(creds_dict.keys())}")
                    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    return None
            elif "google_credentials" in st.secrets:
                print("✅ Found google_credentials")
                creds_dict = dict(st.secrets["google_credentials"])
                print(f"✅ Loaded with keys: {list(creds_dict.keys())}")
                return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
            else:
                print("❌ No Google credentials found in secrets!")
                print(f"Available: {list(st.secrets.keys())}")
                return None
        else:
            # Local development
            if os.path.exists("credentials.json"):
                print("✅ Using local credentials.json")
                return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
            else:
                print("❌ credentials.json not found!")
                return None
                
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_sheet():
    """Get the Google Sheet."""
    try:
        creds = get_credentials()
        if creds is None:
            print("❌ Credentials is None")
            return None
        
        print("🔍 Authorizing client...")
        client = gspread.authorize(creds)
        print("✅ Client authorized")
        
        print(f"🔍 Opening sheet: {SHEET_NAME}")
        sheet = client.open(SHEET_NAME).sheet1
        print(f"✅ Connected to sheet: {SHEET_NAME}")
        return sheet
    except gspread.SpreadsheetNotFound as e:
        print(f"❌ Spreadsheet '{SHEET_NAME}' not found!")
        print("   Make sure you created it and shared with the service account")
        return None
    except Exception as e:
        print(f"❌ Error connecting to sheet: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_feedback_sheet(url, risk, verdict, comment=""):
    """Save feedback to Google Sheets."""
    try:
        print(f"🔍 Saving: {url} -> {verdict}")
        sheet = get_sheet()
        if sheet is None:
            print("❌ Sheet is None - cannot save")
            return False
        
        row = [url, risk, verdict, comment, datetime.now().isoformat()]
        print(f"📝 Row: {row}")
        sheet.append_row(row)
        print(f"✅ Saved: {url} -> {verdict}")
        return True
    except Exception as e:
        print(f"❌ Error saving: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_feedback_sheet():
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
    try:
        df = get_feedback_sheet()
        return len(df)
    except Exception as e:
        print(f"❌ Error getting count: {e}")
        return 0