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
    try:
        # FOR DEPLOYED APP: Use Streamlit secrets
        if os.getenv("STREAMLIT_CLOUD") or os.getenv("STREAMLIT_SHARING"):
            try:
                if "google_credentials" in st.secrets:
                    print("✅ Using google_credentials from secrets")
                    creds_dict = dict(st.secrets["google_credentials"])
                    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
                elif "google_credentials_raw" in st.secrets:
                    print("✅ Using google_credentials_raw from secrets")
                    creds_dict = json.loads(st.secrets["google_credentials_raw"])
                    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
            except Exception as e:
                print(f"Error reading secrets: {e}")
                return None
        
        # FOR LOCAL DEVELOPMENT: Use credentials.json file
        if os.path.exists("credentials.json"):
            print("✅ Using local credentials.json")
            return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
        
        print("❌ No credentials found!")
        return None
        
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

def get_sheet():
    try:
        creds = get_credentials()
        if creds is None:
            return None
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_feedback_sheet(url, risk, verdict, comment=""):
    try:
        sheet = get_sheet()
        if sheet is None:
            print("❌ Sheet not available")
            return False
        row = [url, risk, verdict, comment, datetime.now().isoformat()]
        sheet.append_row(row)
        print(f"✅ Saved: {url}")
        return True
    except Exception as e:
        print(f"Error saving: {e}")
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
        print(f"Error reading: {e}")
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])

def get_feedback_count_sheet():
    try:
        df = get_feedback_sheet()
        return len(df)
    except:
        return 0