"""
URL Phishing Detection Module - ShopShield AI
Developed by Naim Shaikh
"""

import urllib.parse
import pickle
import pandas as pd
import re
import math
import os
from collections import Counter

MODEL_PATH = os.path.join("models", "url_phishing_model.pkl")

SAFE_DOMAINS = [
    'stackoverflow.com', 'github.com', 'amazon.com', 'google.com',
    'microsoft.com', 'apple.com', 'netflix.com', 'spotify.com',
    'nike.com', 'myntra.com', 'boat-lifestyle.com', 'blinkit.com',
    'flipkart.com', 'ajio.com', 'nykaa.com', 'zara.com', 'hm.com',
    'adidas.com', 'puma.com', 'reebok.com', 'underarmour.com',
    'walmart.com', 'target.com', 'bestbuy.com', 'costco.com',
    'youtube.com', 'reddit.com', 'twitter.com', 'linkedin.com',
    'facebook.com', 'instagram.com', 'python.org', 'wikipedia.org',
    'dropbox.com', 'salesforce.com', 'adobe.com', 'oracle.com', 'nykaa.com'
]

SUSPICIOUS_TLDS = [
    '.xyz', '.top', '.club', '.online', '.site', '.win', '.bid',
    '.tk', '.ml', '.ga', '.cf', '.gq', '.click', '.download', '.biz', '.info',
    '.stream', '.date', '.men', '.loan', '.racing', '.review', '.trade'
]

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "account", "secure", "payment", "free", "wallet",
    "bank", "confirm", "update", "validate", "authenticate", "password",
    "reset", "recover", "security", "access", "gift", "offer"
]

BRAND_PATTERNS = [
    "paypal", "amazon", "microsoft", "apple", "google",
    "facebook", "netflix", "spotify"
]

SUSPICIOUS_PATHS = [
    "/verify", "/login", "/account", "/secure", "/confirm", "/update", "/reset"
]

SHORTENING_SERVICES = [
    "bit.ly", "tinyurl", "goo.gl", "short.link", "is.gd",
    "tiny.cc", "ow.ly", "buff.ly"
]

SCAM_PATTERNS = [
    "free-gift", "free-offer", "gift-offer", "bonus-offer",
    "win-prize", "claim-prize", "lucky-winner", "freebie",
    "gift-card", "freebie", "prize", "sweepstakes"
]

UNUSUAL_PORTS = [":8080", ":8443", ":3000", ":5000", ":8000", ":8888", ":4443"]
IP_PATTERN = r"(\d{1,3}\.){3}\d{1,3}"

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
        print(f"Model loaded from {MODEL_PATH}")
        print(f"Expected features: {model.n_features_in_}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None


def calculate_entropy(text):
    counter = Counter(text)
    length = len(text)
    entropy = 0.0
    for count in counter.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return entropy


def extract_features_from_url(url):
    url = url.strip().lower()
    parsed = urllib.parse.urlparse(url)
    
    url_length = len(url)
    num_dots = url.count(".")
    has_https = 1 if parsed.scheme == "https" else 0
    has_ip = 1 if re.search(IP_PATTERN, parsed.netloc) else 0
    
    has_unusual_port = 0
    port_match = re.search(r":(\d+)", parsed.netloc)
    if port_match:
        port = int(port_match.group(1))
        if port not in [80, 443]:
            has_unusual_port = 1
    
    num_subdirs = parsed.path.count("/")
    num_params = len(parsed.query.split("&")) if parsed.query else 0
    
    path_and_query = parsed.path + parsed.query
    suspicious_words = sum(1 for word in SUSPICIOUS_KEYWORDS if word in path_and_query)
    
    special_char_count = sum(
        url.count(c) for c in ["-", "@", "_", "?", "=", "%", "&"]
    )
    
    digits_count = sum(ch.isdigit() for ch in url)
    
    feature_df = pd.DataFrame({
        "url_length": [url_length],
        "num_dots": [num_dots],
        "has_https": [has_https],
        "has_ip": [has_ip],
        "num_subdirs": [num_subdirs],
        "num_params": [num_params],
        "suspicious_words": [suspicious_words],
        "special_char_count": [special_char_count],
        "digits_count": [digits_count]
    })
    
    extra_features = {
        "has_unusual_port": has_unusual_port,
        "has_ip": has_ip,
        "suspicious_words": suspicious_words,
        "url_length": url_length,
        "digits_count": digits_count,
        "num_subdirs": num_subdirs,
        "has_https": has_https,
        "num_dots": num_dots,
        "entropy": calculate_entropy(url),
        "domain": parsed.netloc,
        "path": parsed.path,
        "query": parsed.query
    }
    
    return feature_df, extra_features


def is_legitimate_ecommerce(url_lower, domain):
    legitimate_patterns = [
        r'nike\.com/.*/t/',
        r'myntra\.com/',
        r'boat-lifestyle\.com/',
        r'blinkit\.com/',
        r'amazon\.[a-z]+/',
        r'flipkart\.com/',
        r'ajio\.com/',
        r'nykaa\.com/',
        r'zara\.com/',
        r'hm\.com/',
        r'adidas\.com/',
        r'puma\.com/',
        r'reebok\.com/',
        r'underarmour\.com/',
        r'walmart\.com/',
        r'target\.com/',
        r'bestbuy\.com/',
        r'costco\.com/',
    ]
    
    for pattern in legitimate_patterns:
        if re.search(pattern, url_lower):
            return True
    return False


def is_brand_impersonation(url_lower, domain):
    for brand in BRAND_PATTERNS:
        if brand in url_lower:
            if brand in domain:
                if domain == brand + ".com" or domain == brand + ".in" or domain == brand + ".co.in":
                    return False
                if domain.endswith("." + brand + ".com") or domain.endswith("." + brand + ".in"):
                    return False
            if any(sus in url_lower for sus in ["verify", "login", "account", "secure", "update"]):
                return True
    return False


def heuristic_analysis(url):
    url_lower = url.lower()
    risk = 0.0
    
    if re.search(IP_PATTERN, url_lower):
        risk += 40
    
    if any(port in url_lower for port in UNUSUAL_PORTS):
        risk += 25
    
    if any(tld in url_lower for tld in SUSPICIOUS_TLDS):
        risk += 20
    
    keyword_count = sum(1 for word in SUSPICIOUS_KEYWORDS if word in url_lower)
    if keyword_count >= 3:
        risk += 15
    elif keyword_count >= 2:
        risk += 10
    elif keyword_count >= 1:
        risk += 5
    
    for brand in BRAND_PATTERNS:
        if brand in url_lower:
            if any(sus in url_lower for sus in ["verify", "login", "account", "secure", "update"]):
                risk += 15
                break
    
    if not url_lower.startswith("https://"):
        risk += 10
    
    if len(url_lower) > 80:
        risk += 5
    elif len(url_lower) < 15:
        risk += 5
    
    digit_count = sum(c.isdigit() for c in url_lower)
    if digit_count > 8:
        risk += 10
    
    if url_lower.count("-") > 3:
        risk += 5
    
    if any(path in url_lower for path in SUSPICIOUS_PATHS):
        risk += 8
    
    if "@" in url_lower:
        risk += 15
    
    if any(service in url_lower for service in SHORTENING_SERVICES):
        risk += 15
    
    if any(pattern in url_lower for pattern in SCAM_PATTERNS):
        risk += 20
    
    return min(100.0, risk)


def predict_url_risk(url):
    """
    Predict phishing risk using a combination of ML model and heuristic analysis.
    """
    try:
        url_lower = url.lower()
        domain = urllib.parse.urlparse(url).netloc.lower()
        
        # 1. WHITELIST CHECK - Immediate safe return
        for safe_domain in SAFE_DOMAINS:
            if domain == safe_domain or domain.endswith('.' + safe_domain):
                print(f"Whitelisted safe domain: {domain}")
                return 5.0
        
        # 2. LEGITIMATE E-COMMERCE CHECK
        if is_legitimate_ecommerce(url_lower, domain):
            print(f"Legitimate e-commerce site: {domain}")
            return 8.0
        
        # 3. HEURISTIC ANALYSIS FIRST
        heuristic_risk = heuristic_analysis(url)
        print(f"Heuristic risk: {heuristic_risk}%")
        
        # If heuristic says safe, return safe
        if heuristic_risk < 30:
            print(f"URL appears safe based on heuristic analysis")
            return heuristic_risk
        
        # 4. ML MODEL PREDICTION (if available)
        if model is not None:
            try:
                features, extra_features = extract_features_from_url(url)
                
                if features.shape[1] == model.n_features_in_:
                    probabilities = model.predict_proba(features)[0]
                    
                    if hasattr(model, 'classes_'):
                        classes = list(model.classes_)
                        if 1 in classes:
                            phishing_prob = probabilities[classes.index(1)]
                        else:
                            phishing_prob = probabilities[0]
                    else:
                        phishing_prob = probabilities[1] if len(probabilities) > 1 else probabilities[0]
                    
                    ml_risk = float(round(phishing_prob * 100, 2))
                    print(f"ML risk: {ml_risk}%")
                    
                    # Combine heuristic and ML (weighted average)
                    # Give more weight to heuristic for safety
                    if heuristic_risk >= 70 and ml_risk >= 70:
                        final_risk = max(heuristic_risk, ml_risk)
                    elif heuristic_risk >= 50 and ml_risk >= 50:
                        final_risk = (heuristic_risk * 0.6) + (ml_risk * 0.4)
                    else:
                        final_risk = heuristic_risk
                    
                    final_risk = min(100.0, final_risk)
                    print(f"Final risk: {final_risk}%")
                    return final_risk
                    
            except Exception as e:
                print(f"ML prediction error: {e}")
        
        # 5. If ML fails, return heuristic
        print(f"Using heuristic risk: {heuristic_risk}%")
        return heuristic_risk
        
    except Exception as e:
        print(f"Prediction Error: {e}")
        return heuristic_analysis(url)


def predict_batch_risk(urls):
    """Predict risk for multiple URLs."""
    return {url: predict_url_risk(url) for url in urls}


def get_model_info():
    """Get information about the loaded model."""
    if model is None:
        return {"status": "Not loaded"}
    
    return {
        "status": "Loaded",
        "type": type(model).__name__,
        "features": model.n_features_in_,
        "classes": model.classes_.tolist() if hasattr(model, 'classes_') else "Unknown",
        "has_class_weight": hasattr(model, 'class_weight')
    }


if __name__ == "__main__":
    print("=" * 70)
    print("Testing URL Analyzer")
    print("=" * 70)
    
    test_urls = [
        "https://www.nike.com/in/t/air-max-shoes-PmlK0x",
        "https://www.myntra.com/men-casual-shirts",
        "https://www.boat-lifestyle.com/collections/wireless-earphones",
        "https://www.blinkit.com/categories/grocery-staples",
        "https://www.amazon.com",
        "https://www.google.com",
        "https://github.com",
        "http://103.20.213.34:8080/free-shop-login",
        "http://192.168.1.1/login",
        "https://secure-paypal-verify.xyz",
        "http://free-gift-offer.biz",
    ]
    
    print("\nPredictions:")
    print("-" * 70)
    
    for url in test_urls:
        risk = predict_url_risk(url)
        
        if risk >= 70:
            status = "🔴 PHISHING"
        elif risk >= 30:
            status = "🟡 SUSPICIOUS"
        else:
            status = "🟢 SAFE"
        
        print(f"{status}: {url[:50]}... ({risk:.1f}%)")
        print()
    
    print("=" * 70)
    print("\nModel Info:")
    print(get_model_info())
    print("=" * 70)