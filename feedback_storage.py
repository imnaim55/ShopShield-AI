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
    """
    Get credentials from Streamlit Secrets (deployed) or local file (development).
    """
    try:
        # Check if running on Streamlit Cloud
        if os.getenv("STREAMLIT_CLOUD") or os.getenv("STREAMLIT_SHARING"):
            # Use Streamlit Secrets (deployed)
            try:
                # Access the google_credentials section from secrets
                creds_dict = dict(st.secrets["google_credentials"])
                return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
            except Exception as e:
                print(f"Error loading from secrets: {e}")
                return None
        else:
            # Use local file (development)
            if os.path.exists("credentials.json"):
                return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
            else:
                print("credentials.json not found! Please create it or use Streamlit secrets.")
                return None
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

def get_sheet():
    """Get the Google Sheet with error handling."""
    try:
        creds = get_credentials()
        if creds is None:
            print("❌ Could not load credentials")
            return None
        
        client = gspread.authorize(creds)
        print("✅ Authorized successfully")
        
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