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
import traceback

SHEET_NAME = "ShopShield Feedback"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_credentials():
    """Get credentials from Streamlit Secrets or local file."""
    try:
        # Check if running on Streamlit Cloud
        if os.getenv("STREAMLIT_CLOUD") or os.getenv("STREAMLIT_SHARING"):
            st.write("🔍 Running on Streamlit Cloud")
            
            # Debug: Show what's in secrets (remove after testing)
            st.write(f"📋 Secrets keys: {list(st.secrets.keys())}")
            
            if "google_credentials_raw" in st.secrets:
                st.write("✅ Found google_credentials_raw")
                try:
                    creds_dict = json.loads(st.secrets["google_credentials_raw"])
                    st.write(f"✅ Loaded JSON with keys: {list(creds_dict.keys())}")
                    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON decode error: {e}")
                    return None
            elif "google_credentials" in st.secrets:
                st.write("✅ Found google_credentials")
                creds_dict = dict(st.secrets["google_credentials"])
                st.write(f"✅ Loaded with keys: {list(creds_dict.keys())}")
                return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
            else:
                st.error("❌ No Google credentials found in secrets!")
                st.write(f"Available: {list(st.secrets.keys())}")
                return None
        else:
            # Local development
            if os.path.exists("credentials.json"):
                st.write("✅ Using local credentials.json")
                return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
            else:
                st.error("❌ credentials.json not found!")
                return None
                
    except Exception as e:
        st.error(f"❌ Error loading credentials: {e}")
        st.code(traceback.format_exc())
        return None

def get_sheet():
    """Get the Google Sheet."""
    try:
        creds = get_credentials()
        if creds is None:
            st.error("❌ Credentials is None")
            return None
        
        st.write("🔍 Authorizing client...")
        client = gspread.authorize(creds)
        st.write("✅ Client authorized")
        
        st.write(f"🔍 Opening sheet: {SHEET_NAME}")
        sheet = client.open(SHEET_NAME).sheet1
        st.write(f"✅ Connected to sheet: {SHEET_NAME}")
        return sheet
    except gspread.SpreadsheetNotFound as e:
        st.error(f"❌ Spreadsheet '{SHEET_NAME}' not found!")
        st.write("   Make sure you created it and shared with the service account")
        st.code(traceback.format_exc())
        return None
    except Exception as e:
        st.error(f"❌ Error connecting to sheet: {e}")
        st.code(traceback.format_exc())
        return None

def save_feedback_sheet(url, risk, verdict, comment=""):
    """Save feedback to Google Sheets."""
    try:
        st.write(f"🔍 Saving: {url} -> {verdict}")
        sheet = get_sheet()
        if sheet is None:
            st.error("❌ Sheet is None - cannot save")
            return False
        
        row = [url, risk, verdict, comment, datetime.now().isoformat()]
        st.write(f"📝 Row: {row}")
        sheet.append_row(row)
        st.success(f"✅ Saved: {url} -> {verdict}")
        return True
    except Exception as e:
        st.error(f"❌ Error saving: {e}")
        st.code(traceback.format_exc())
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
        st.error(f"❌ Error reading: {e}")
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])

def get_feedback_count_sheet():
    try:
        df = get_feedback_sheet()
        return len(df)
    except Exception as e:
        st.error(f"❌ Error getting count: {e}")
        return 0