"""
Domain Analysis Module - ShopShield AI
Developed by Naim Shaikh
"""

import whois
from datetime import datetime, timezone
import re
import pytz

def get_domain_metadata(url):
    try:
        domain = extract_domain(url)
        
        if not domain:
            return get_default_metadata(url)
        
        w = whois.whois(domain)
        
        result = {
            'domain_age_days': -1,
            'days_until_expiry': -1,
            'has_registrar': 0,
            'is_private_registered': 0,
            'domain': domain,
            'creation_date': None,
            'expiration_date': None,
            'registrar': None,
            'whois_success': 1
        }
        
        if w.creation_date:
            if isinstance(w.creation_date, list):
                creation_date = w.creation_date[0]
            else:
                creation_date = w.creation_date
            
            if creation_date.tzinfo:
                now = datetime.now(timezone.utc)
                result['domain_age_days'] = (now - creation_date).days
            else:
                result['domain_age_days'] = (datetime.now() - creation_date).days
            
            result['creation_date'] = creation_date
            
        if w.expiration_date:
            if isinstance(w.expiration_date, list):
                expiry_date = w.expiration_date[0]
            else:
                expiry_date = w.expiration_date
            
            if expiry_date.tzinfo:
                now = datetime.now(timezone.utc)
                result['days_until_expiry'] = (expiry_date - now).days
            else:
                result['days_until_expiry'] = (expiry_date - datetime.now()).days
                
            result['expiration_date'] = expiry_date
            
        result['has_registrar'] = 1 if w.registrar else 0
        result['registrar'] = w.registrar if w.registrar else None
        
        if w.name and 'privacy' in str(w.name).lower():
            result['is_private_registered'] = 1
            
        if w.org and 'privacy' in str(w.org).lower():
            result['is_private_registered'] = 1
        
        return result
        
    except Exception as e:
        print(f"Domain analysis error: {e}")
        return get_fallback_metadata(extract_domain(url))


def get_default_metadata(url):
    domain = extract_domain(url)
    return {
        'domain_age_days': -1,
        'days_until_expiry': -1,
        'has_registrar': 0,
        'is_private_registered': 0,
        'domain': domain,
        'creation_date': None,
        'expiration_date': None,
        'registrar': None,
        'whois_success': 0
    }


def get_fallback_metadata(domain):
    return {
        'domain_age_days': -1,
        'days_until_expiry': -1,
        'has_registrar': 0,
        'is_private_registered': 0,
        'domain': domain,
        'creation_date': None,
        'expiration_date': None,
        'registrar': None,
        'whois_success': 0
    }


def extract_domain(url):
    try:
        url = url.strip().lower()
        if '://' in url:
            url = url.split('://')[1]
        if '/' in url:
            url = url.split('/')[0]
        if ':' in url:
            url = url.split(':')[0]
        if '@' in url:
            url = url.split('@')[1]
        
        if url.startswith('www.'):
            url = url[4:]
        
        return url
    except:
        return None


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
    
    if metadata['whois_success'] == 0:
        domain = extract_domain(url)
        return f"Domain: {domain if domain else 'Unknown'} (WHOIS information unavailable - domain may be new or blocked)"
    
    if metadata['domain_age_days'] == -1:
        return f"Domain: {metadata['domain']} (Age information unavailable)"
    
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
    
    registrar_text = f", Registrar: {metadata['registrar']}" if metadata['registrar'] else ""
    private_text = " (Private Registration)" if metadata['is_private_registered'] == 1 else ""
    
    if metadata['creation_date']:
        try:
            date_text = metadata['creation_date'].strftime('%Y-%m-%d')
            return f"Domain: {metadata['domain']}, Created: {date_text}, Age: {age_text}{private_text}{registrar_text}"
        except:
            return f"Domain: {metadata['domain']}, Age: {age_text}{private_text}{registrar_text}"
    else:
        return f"Domain: {metadata['domain']}, Age: {age_text}{private_text}{registrar_text}"