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

def get_sheet():
    """Get the Google Sheet with error handling."""
    try:
        if os.getenv("STREAMLIT_CLOUD"):
            # Read from Streamlit secrets
            creds_dict = dict(st.secrets["google_credentials"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        else:
            # Local development - read from file
            if not os.path.exists("credentials.json"):
                print("❌ credentials.json not found!")
                return None
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
        
        client = gspread.authorize(creds)
        
        # Try to open the sheet
        try:
            sheet = client.open(SHEET_NAME).sheet1
            print(f"✅ Opened sheet: {SHEET_NAME}")
            return sheet
        except gspread.SpreadsheetNotFound:
            print(f"❌ Spreadsheet '{SHEET_NAME}' not found!")
            print("   Make sure you created it and shared with the service account")
            return None
            
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return None

def save_feedback_sheet(url, risk, verdict, comment=""):
    """Save feedback to Google Sheets."""
    try:
        sheet = get_sheet()
        if sheet is None:
            print("❌ Could not get sheet")
            return False
        
        # Create row
        row = [url, risk, verdict, comment, datetime.now().isoformat()]
        
        # Append to sheet
        sheet.append_row(row)
        print(f"✅ Feedback saved: {url} -> {verdict}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving feedback: {e}")
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
        print(f"❌ Error reading feedback: {e}")
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])

def get_feedback_count_sheet():
    """Get number of feedback entries."""
    try:
        df = get_feedback_sheet()
        return len(df)
    except:
        return 0

if __name__ == "__main__":
    print("Testing Google Sheets save...")
    result = save_feedback_sheet(
        url="https://test.com",
        risk=50,
        verdict="safe",
        comment="Test entry"
    )
    print(f"Result: {result}")