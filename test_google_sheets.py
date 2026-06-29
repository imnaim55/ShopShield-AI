"""
Test Google Sheets Connection
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def test_connection():
    """Test Google Sheets connection."""
    try:
        print("1. Looking for credentials.json...")
        if not os.path.exists("credentials.json"):
            print("❌ credentials.json not found!")
            return False
        
        print("2. Loading credentials...")
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
        print("✅ Credentials loaded")
        
        print("3. Authorizing client...")
        client = gspread.authorize(creds)
        print("✅ Client authorized")
        
        print("4. Opening spreadsheet...")
        try:
            sheet = client.open("ShopShield Feedback").sheet1
            print("✅ Spreadsheet opened")
            
            print("5. Getting all records...")
            records = sheet.get_all_records()
            print(f"✅ Found {len(records)} records")
            
            print("\n📊 Connection successful!")
            return True
            
        except gspread.SpreadsheetNotFound:
            print("❌ Spreadsheet 'ShopShield Feedback' not found!")
            print("   Please create it and share with:")
            print("   shopshield-feedback@norse-acrobat-439117-e7.iam.gserviceaccount.com")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Type: {type(e)}")
        return False

def test_save():
    """Test saving to Google Sheets."""
    try:
        print("\nTesting save...")
        from feedback_storage import save_feedback_sheet
        
        result = save_feedback_sheet(
            url="https://test.com",
            risk=50,
            verdict="safe",
            comment="Test from script"
        )
        
        if result:
            print("✅ Save successful!")
        else:
            print("❌ Save failed")
        return result
        
    except Exception as e:
        print(f"❌ Error saving: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Google Sheets Test")
    print("=" * 60)
    
    # Test connection
    connection_ok = test_connection()
    
    # If connection works, test save
    if connection_ok:
        test_save()