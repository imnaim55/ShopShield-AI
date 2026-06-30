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

def get_client():
    """Get authorized gspread client."""
    try:
        # Check if running on Streamlit Cloud
        if os.getenv("STREAMLIT_CLOUD") or os.getenv("STREAMLIT_SHARING"):
            # Use Streamlit Secrets
            if "google_credentials_raw" in st.secrets:
                creds_dict = json.loads(st.secrets["google_credentials_raw"])
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
                return gspread.authorize(creds)
            elif "google_credentials" in st.secrets:
                creds_dict = dict(st.secrets["google_credentials"])
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
                return gspread.authorize(creds)
            else:
                st.error("Google credentials not found in secrets!")
                return None
        else:
            # Local development
            if os.path.exists("credentials.json"):
                creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
                return gspread.authorize(creds)
            else:
                st.error("credentials.json not found!")
                return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def save_feedback_sheet(url, risk, verdict, comment=""):
    """Save feedback to Google Sheets."""
    try:
        client = get_client()
        if client is None:
            return False
        
        # Open the sheet
        sheet = client.open(SHEET_NAME).sheet1
        
        # Append row
        row = [url, risk, verdict, comment, datetime.now().isoformat()]
        sheet.append_row(row)
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False

def get_feedback_sheet():
    """Get all feedback from Google Sheets."""
    try:
        client = get_client()
        if client is None:
            return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
        
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
    except Exception as e:
        print(f"Error reading: {e}")
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])

def get_feedback_count_sheet():
    """Get number of feedback entries."""
    try:
        df = get_feedback_sheet()
        return len(df)
    except:
        return 0

def debug_connection():
    """Debug function to test Google Sheets connection."""
    try:
        client = get_client()
        if client is None:
            return "❌ Client is None"
        
        sheet = client.open(SHEET_NAME).sheet1
        return f"✅ Connected to {SHEET_NAME}"
    except Exception as e:
        return f"❌ Error: {e}"