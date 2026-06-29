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

# Google Sheets setup
SHEET_NAME = "ShopShield Feedback"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_sheet():
    """Get the Google Sheet."""
    try:
        # For deployed app - use secrets
        if os.getenv("STREAMLIT_CLOUD"):
            import json
            creds_dict = st.secrets["google_credentials"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        else:
            # Local development
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
        
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None

def save_feedback_sheet(url, risk, verdict, comment=""):
    """Save feedback to Google Sheets."""
    try:
        sheet = get_sheet()
        if sheet is None:
            return False
        
        # Append new row
        row = [url, risk, verdict, comment, datetime.now().isoformat()]
        sheet.append_row(row)
        print(f"✅ Feedback saved to Google Sheets: {url}")
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
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
        print(f"Error reading feedback: {e}")
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])

def get_feedback_count_sheet():
    """Get number of feedback entries."""
    try:
        df = get_feedback_sheet()
        return len(df)
    except:
        return 0