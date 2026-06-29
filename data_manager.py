"""
Data Management Module - ShopShield AI
Developed by Naim Shaikh
"""

import os
import json
import base64
import requests
import pandas as pd
from io import StringIO
from datetime import datetime  # <-- ADD THIS IMPORT

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set in Streamlit Cloud Secrets
REPO_OWNER = "imnaim55"  # Replace with your GitHub username
REPO_NAME = "ShopShield-AI"  # Replace with your repository name
FILE_PATH = "data/user_feedback.csv"
BRANCH = "main"

def read_feedback():
    """Read feedback from GitHub."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content['content']).decode('utf-8')
            return pd.read_csv(StringIO(decoded))
        else:
            # File doesn't exist yet
            return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])
    except Exception as e:
        print(f"Error reading feedback: {e}")
        return pd.DataFrame(columns=['url', 'risk_score', 'verdict', 'comment', 'timestamp'])

def write_feedback(df):
    """Write feedback to GitHub."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Convert DataFrame to CSV string
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    content = base64.b64encode(csv_buffer.getvalue().encode('utf-8')).decode('utf-8')
    
    # Get current file SHA if it exists
    sha = None
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            sha = response.json()['sha']
    except:
        pass
    
    # Prepare payload
    payload = {
        "message": "Update user feedback",
        "content": content,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error writing feedback: {e}")
        return False

def save_feedback_cloud(url, risk, verdict, comment=""):
    """Save user feedback using GitHub storage."""
    try:
        # Read existing feedback
        df = read_feedback()
        
        # Create new entry
        new_entry = pd.DataFrame([{
            "url": url,
            "risk_score": risk,
            "verdict": verdict,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }])
        
        # Append and save
        df = pd.concat([df, new_entry], ignore_index=True)
        return write_feedback(df)
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False