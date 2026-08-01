"""
Content Fetcher Module - ShopShield AI
Developed by Naim Shaikh
"""

import requests
from bs4 import BeautifulSoup
import re

def fetch_website_content(url):
    """
    Fetch and extract text content from a website URL.
    Returns extracted text or error message.
    """
    try:
        # Add headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Limit to first 5000 characters (for performance)
        if len(text) > 5000:
            text = text[:5000] + "... [truncated]"
        
        return text, None
        
    except requests.exceptions.Timeout:
        return None, "Timeout: Website took too long to respond"
    except requests.exceptions.ConnectionError:
        return None, "Connection Error: Could not reach the website"
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP Error: {e.response.status_code}"
    except Exception as e:
        return None, f"Error: {str(e)}"