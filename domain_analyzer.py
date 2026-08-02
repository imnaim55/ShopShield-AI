"""
Domain Analysis Module - ShopShield AI
Developed by Naim Shaikh
"""

import whois
from datetime import datetime
import re

def get_domain_metadata(url):
    try:
        domain = extract_domain(url)
        w = whois.whois(domain)
        
        result = {
            'domain_age_days': -1,
            'days_until_expiry': -1,
            'has_registrar': 0,
            'is_private_registered': 0,
            'domain': domain,
            'creation_date': None,
            'expiration_date': None,
            'registrar': None
        }
        
        if w.creation_date:
            if isinstance(w.creation_date, list):
                creation_date = w.creation_date[0]
            else:
                creation_date = w.creation_date
            result['creation_date'] = creation_date
            result['domain_age_days'] = (datetime.now() - creation_date).days
            
        if w.expiration_date:
            if isinstance(w.expiration_date, list):
                expiry_date = w.expiration_date[0]
            else:
                expiry_date = w.expiration_date
            result['expiration_date'] = expiry_date
            result['days_until_expiry'] = (expiry_date - datetime.now()).days
            
        result['has_registrar'] = 1 if w.registrar else 0
        result['registrar'] = w.registrar if w.registrar else None
        
        if w.name and 'privacy' in str(w.name).lower():
            result['is_private_registered'] = 1
            
        if w.org and 'privacy' in str(w.org).lower():
            result['is_private_registered'] = 1
            
        return result
        
    except Exception as e:
        print(f"Domain analysis error: {e}")
        return {
            'domain_age_days': -1,
            'days_until_expiry': -1,
            'has_registrar': 0,
            'is_private_registered': 0,
            'domain': extract_domain(url),
            'creation_date': None,
            'expiration_date': None,
            'registrar': None
        }

def extract_domain(url):
    url = url.strip().lower()
    if '://' in url:
        url = url.split('://')[1]
    if '/' in url:
        url = url.split('/')[0]
    if ':' in url:
        url = url.split(':')[0]
    if '@' in url:
        url = url.split('@')[1]
    return url

def get_domain_risk_score(url):
    metadata = get_domain_metadata(url)
    
    if metadata['domain_age_days'] == -1:
        return 0
    
    risk = 0
    
    if metadata['domain_age_days'] < 30:
        risk += 25
    elif metadata['domain_age_days'] < 90:
        risk += 15
    elif metadata['domain_age_days'] < 180:
        risk += 8
    
    if metadata['days_until_expiry'] < 30 and metadata['days_until_expiry'] > 0:
        risk += 15
    elif metadata['days_until_expiry'] < 90 and metadata['days_until_expiry'] > 0:
        risk += 8
    
    if metadata['is_private_registered'] == 1:
        risk += 10
    
    if metadata['has_registrar'] == 0:
        risk += 5
    
    return min(100, risk)

def is_new_domain(url):
    metadata = get_domain_metadata(url)
    if metadata['domain_age_days'] == -1:
        return False
    return metadata['domain_age_days'] < 90

def get_domain_summary(url):
    metadata = get_domain_metadata(url)
    if metadata['domain_age_days'] == -1:
        return "Domain information unavailable"
    
    parts = []
    if metadata['domain_age_days'] > 0:
        years = metadata['domain_age_days'] // 365
        months = (metadata['domain_age_days'] % 365) // 30
        if years > 0:
            parts.append(f"{years} year{'s' if years > 1 else ''}")
        if months > 0:
            parts.append(f"{months} month{'s' if months > 1 else ''}")
        if not parts:
            parts.append(f"{metadata['domain_age_days']} days")
        age_text = " ".join(parts)
    else:
        age_text = "Unknown"
    
    return f"Domain: {metadata['domain']}, Age: {age_text}, Registered: {metadata['creation_date'].strftime('%Y-%m-%d') if metadata['creation_date'] else 'Unknown'}"