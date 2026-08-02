"""
SSL Analysis Module - ShopShield AI
Developed by Naim Shaikh
"""

import ssl
import socket
from datetime import datetime
import urllib.parse

def check_ssl_certificate(url):
    try:
        domain = extract_domain(url)
        
        if not domain:
            return {
                'has_ssl': 0,
                'ssl_days_left': -1,
                'ssl_issuer': None,
                'ssl_subject': None,
                'ssl_valid': 0
            }
        
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                if cert:
                    expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_left = (expiry - datetime.now()).days
                    
                    return {
                        'has_ssl': 1,
                        'ssl_days_left': days_left,
                        'ssl_issuer': cert.get('issuer', ''),
                        'ssl_subject': cert.get('subject', ''),
                        'ssl_valid': 1 if days_left > 0 else 0
                    }
                
    except Exception as e:
        print(f"SSL check error: {e}")
    
    return {
        'has_ssl': 0,
        'ssl_days_left': -1,
        'ssl_issuer': None,
        'ssl_subject': None,
        'ssl_valid': 0
    }

def extract_domain(url):
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        if ':' in domain:
            domain = domain.split(':')[0]
        if '@' in domain:
            domain = domain.split('@')[1]
        return domain
    except:
        return None

def get_ssl_risk_score(url):
    ssl_info = check_ssl_certificate(url)
    
    if ssl_info['has_ssl'] == 0:
        return 25
    
    if not ssl_info['ssl_valid']:
        return 30
    
    risk = 0
    
    if ssl_info['ssl_days_left'] < 30:
        risk += 20
    elif ssl_info['ssl_days_left'] < 90:
        risk += 10
    
    if ssl_info['ssl_issuer'] and 'Let\'s Encrypt' in str(ssl_info['ssl_issuer']):
        risk += 5
    
    return min(100, risk)

def get_ssl_summary(url):
    ssl_info = check_ssl_certificate(url)
    
    if ssl_info['has_ssl'] == 0:
        return "SSL: Not installed (insecure)"
    
    if not ssl_info['ssl_valid']:
        return "SSL: Expired or invalid"
    
    status = "Valid"
    if ssl_info['ssl_days_left'] < 30:
        status = "Expiring soon"
    elif ssl_info['ssl_days_left'] < 90:
        status = "Expiring in {ssl_info['ssl_days_left']} days"
    
    return f"SSL: {status}, Days left: {ssl_info['ssl_days_left']}"