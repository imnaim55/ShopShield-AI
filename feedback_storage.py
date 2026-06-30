"""
Feedback Storage Module - ShopShield AI (Airtable)
Developed by Naim Shaikh
"""

import requests
import pandas as pd
from datetime import datetime
import streamlit as st
import os

# Airtable configuration - get from secrets
def get_airtable_config():
    """Get Airtable configuration from secrets or environment."""
    try:
        if os.getenv("STREAMLIT_CLOUD") or os.getenv("STREAMLIT_SHARING"):
            # Deployed app - use Streamlit secrets
            api_key = st.secrets.get("AIRTABLE_API_KEY")
            base_id = st.secrets.get("AIRTABLE_BASE_ID")
        else:
            # Local development - use environment variables or hardcoded
            api_key = os.getenv("AIRTABLE_API_KEY", "YOUR_API_KEY_HERE")
            base_id = os.getenv("AIRTABLE_BASE_ID", "YOUR_BASE_ID_HERE")
        
        return api_key, base_id
    except Exception as e:
        print(f"Error getting config: {e}")
        return None, None

def save_feedback_sheet(url, risk, verdict, comment=""):
    """Save feedback to Airtable."""
    try:
        api_key, base_id = get_airtable_config()
        if not api_key or not base_id:
            print("❌ Airtable credentials not found")
            return False
        
        url_api = f"https://api.airtable.com/v0/{base_id}/Feedback"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "records": [{
                "fields": {
                    "URL": url,
                    "Risk": risk,
                    "Verdict": verdict,
                    "Comment": comment,
                    "Timestamp": datetime.now().isoformat()
                }
            }]
        }
        
        print(f"📤 Sending to Airtable: {url} -> {verdict}")
        response = requests.post(url_api, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ Saved: {url} -> {verdict}")
            return True
        else:
            print(f"❌ Airtable Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving: {e}")
        return False

def get_feedback_sheet():
    """Get all feedback from Airtable."""
    try:
        api_key, base_id = get_airtable_config()
        if not api_key or not base_id:
            return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
        
        url_api = f"https://api.airtable.com/v0/{base_id}/Feedback"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.get(url_api, headers=headers)
        if response.status_code == 200:
            data = response.json()
            records = data.get("records", [])
            if records:
                rows = []
                for record in records:
                    fields = record.get("fields", {})
                    rows.append({
                        "url": fields.get("URL", ""),
                        "risk_score": fields.get("Risk", 0),
                        "verdict": fields.get("Verdict", ""),
                        "comment": fields.get("Comment", ""),
                        "timestamp": fields.get("Timestamp", "")
                    })
                return pd.DataFrame(rows)
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

def test_connection():
    """Test Airtable connection."""
    try:
        api_key, base_id = get_airtable_config()
        if not api_key or not base_id:
            return "❌ Credentials not found"
        
        url_api = f"https://api.airtable.com/v0/{base_id}/Feedback"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url_api, headers=headers)
        
        if response.status_code == 200:
            return "✅ Connected to Airtable!"
        else:
            return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {e}"