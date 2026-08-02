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
            return get_default_ssl_info()
        
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                if cert and 'notAfter' in cert:
                    expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_left = (expiry - datetime.now()).days
                    
                    return {
                        'has_ssl': 1,
                        'ssl_days_left': days_left,
                        'ssl_issuer': cert.get('issuer', ''),
                        'ssl_subject': cert.get('subject', ''),
                        'ssl_valid': 1 if days_left > 0 else 0
                    }
                
    except socket.gaierror:
        print(f"SSL check: Could not resolve domain")
    except ConnectionRefusedError:
        print(f"SSL check: Connection refused")
    except socket.timeout:
        print(f"SSL check: Connection timeout")
    except Exception as e:
        print(f"SSL check error: {e}")
    
    return get_default_ssl_info()


def get_default_ssl_info():
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
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain if domain else None
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
        return "SSL Certificate: Not installed (insecure connection)"
    
    if not ssl_info['ssl_valid']:
        return "SSL Certificate: Expired or invalid"
    
    if ssl_info['ssl_days_left'] < 30:
        return f"SSL Certificate: Expiring soon ({ssl_info['ssl_days_left']} days left)"
    elif ssl_info['ssl_days_left'] < 90:
        return f"SSL Certificate: Valid ({ssl_info['ssl_days_left']} days left)"
    else:
        return f"SSL Certificate: Valid and secure ({ssl_info['ssl_days_left']} days left)"