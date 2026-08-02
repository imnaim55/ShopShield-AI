"""
URL Phishing Detection Module - ShopShield AI
Developed by Naim Shaikh
"""

import os
import urllib.parse
import pickle
import pandas as pd
import re
import math
from collections import Counter
from huggingface_hub import hf_hub_download
from domain_analyzer import get_domain_risk_score, get_domain_summary, is_new_domain
from ssl_analyzer import get_ssl_risk_score, get_ssl_summary

MODEL_PATH = os.path.join("models", "url_phishing_model.pkl")
HF_MODEL_REPO = "imnaim55/shopshield-model"
HF_MODEL_FILE = "url_phishing_model.pkl"

SAFE_DOMAINS = [
    'amazon.com', 'google.com', 'github.com', 'stackoverflow.com',
    'microsoft.com', 'apple.com', 'netflix.com', 'spotify.com',
    'nike.com', 'myntra.com', 'flipkart.com', 'ajio.com',
    'nykaa.com', 'zara.com', 'hm.com', 'adidas.com', 'puma.com',
    'walmart.com', 'target.com', 'youtube.com', 'reddit.com',
    'twitter.com', 'linkedin.com', 'facebook.com', 'instagram.com',
    'python.org', 'wikipedia.org', 'dropbox.com',
    'paypal.com', 'ebay.com', 'bestbuy.com', 'costco.com',
    'homedepot.com', 'lowes.com', 'macys.com', 'sephora.com'
]

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "account", "secure", "payment", "free",
    "wallet", "bank", "confirm", "update", "validate",
    "authenticate", "password", "reset", "recover", "security",
    "signin", "sign-in", "log-in", "user", "profile",
    "gift", "bonus", "offer", "deal", "promo", "discount",
    "claim", "winner", "prize", "lucky", "congratulations",
    "download", "movie", "film", "stream", "watch", "hd",
    "720p", "1080p", "4k", "bluray", "dvd", "torrent",
    "subtitle", "english", "hindi", "tamil", "telugu",
    "malayalam", "kannada", "punjabi", "bengali",
    "crypto", "bitcoin", "ethereum", "wallet", "investment",
    "loan", "credit", "card", "insurance", "mortgage",
    "job", "career", "interview", "salary", "wfh"
]

SUSPICIOUS_TLDS = [
    '.xyz', '.top', '.club', '.online', '.site', '.win', '.bid',
    '.tk', '.ml', '.ga', '.cf', '.gq', '.click', '.download',
    '.biz', '.info', '.stream', '.date', '.men', '.loan',
    '.racing', '.review', '.trade', '.lol', '.work', '.fun',
    '.zip', '.mov', '.movie', '.download', '.run', '.place', '.rest', '.uno',
    '.cricket', '.football', '.racing', '.store', '.shop', '.host', '.cloud'
]

BRAND_PATTERNS = [
    "paypal", "amazon", "microsoft", "apple", "google",
    "facebook", "netflix", "spotify", "roblox", "instagram",
    "whatsapp", "telegram", "discord", "twitch", "twitter",
    "ebay", "walmart", "target", "bestbuy", "costco",
    "homedepot", "lowes", "macys", "sephora", "nike",
    "adidas", "puma", "zara", "hm", "myntra", "flipkart"
]

SUSPICIOUS_PATHS = [
    "/verify", "/login", "/account", "/secure", "/confirm",
    "/update", "/reset", "/auth", "/signin", "/sign-in",
    "/log-in", "/user", "/profile", "/wallet", "/payment",
    "/bank", "/funds", "/withdraw", "/deposit", "/transfer",
    "/validate", "/authenticate", "/recover", "/password",
    "/reset-password", "/change-password", "/2fa", "/otp"
]

SCAM_PATTERNS = [
    "free-gift", "free-offer", "gift-offer", "bonus-offer",
    "win-prize", "claim-prize", "lucky-winner", "freebie",
    "gift-card", "free-money", "earn-money", "make-money",
    "quick-cash", "easy-money", "get-rich", "investment",
    "referral-bonus", "signup-bonus", "welcome-bonus",
    "limited-time", "act-now", "dont-miss", "hurry-up"
]

UNUSUAL_PORTS = [":8080", ":8443", ":3000", ":5000", ":8000", ":8888", ":4443", ":7000"]
IP_PATTERN = r"(\d{1,3}\.){3}\d{1,3}"


def load_model():
    try:
        print("Loading model from Hugging Face Hub")
        model_path = hf_hub_download(
            repo_id=HF_MODEL_REPO,
            filename=HF_MODEL_FILE,
            repo_type="model"
        )
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        print(f"Model loaded from Hugging Face: {HF_MODEL_REPO}")
        print(f"Features: {model.n_features_in_}")
        print(f"Trees: {model.n_estimators}")
        return model
    except Exception as e:
        print(f"Error loading model from Hugging Face: {e}")
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    model = pickle.load(f)
                print(f"Model loaded locally: {MODEL_PATH}")
                return model
            except Exception as e2:
                print(f"Error loading local model: {e2}")
        print("No model available. Using heuristic analysis only.")
        return None


model = load_model()


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

    special_char_count = sum(url.count(c) for c in ["-", "@", "_", "?", "=", "%", "&"])
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


def heuristic_analysis(url):
    url_lower = url.lower()
    risk = 0.0

    if re.search(IP_PATTERN, url_lower):
        risk += 55

    if any(port in url_lower for port in UNUSUAL_PORTS):
        risk += 40

    if any(tld in url_lower for tld in SUSPICIOUS_TLDS):
        risk += 30

    keyword_count = sum(1 for word in SUSPICIOUS_KEYWORDS if word in url_lower)
    if keyword_count >= 4:
        risk += 35
    elif keyword_count >= 3:
        risk += 25
    elif keyword_count >= 2:
        risk += 15
    elif keyword_count >= 1:
        risk += 8

    for brand in BRAND_PATTERNS:
        if brand in url_lower:
            if any(sus in url_lower for sus in ["verify", "login", "account", "secure", "update"]):
                risk += 35
                break

    if not url_lower.startswith("https://"):
        risk += 15

    if any(path in url_lower for path in SUSPICIOUS_PATHS):
        risk += 20

    if "@" in url_lower:
        risk += 25

    if any(pattern in url_lower for pattern in SCAM_PATTERNS):
        risk += 30

    if len(url_lower) > 100:
        risk += 10

    if url_lower.count("-") > 4:
        risk += 10

    if sum(c.isdigit() for c in url_lower) > 8:
        risk += 10

    return min(100.0, risk)


def predict_url_risk(url):
    try:
        url_lower = url.lower()
        domain = urllib.parse.urlparse(url).netloc.lower()

        for safe_domain in SAFE_DOMAINS:
            if domain == safe_domain or domain.endswith('.' + safe_domain):
                print(f"Safe domain: {domain}")
                return 5.0

        heuristic_risk = heuristic_analysis(url)
        print(f"Heuristic risk: {heuristic_risk}%")

        if heuristic_risk >= 60:
            print(f"High risk from heuristic: {heuristic_risk}%")
            return heuristic_risk

        domain_risk = get_domain_risk_score(url)
        print(f"Domain risk: {domain_risk}%")

        ssl_risk = get_ssl_risk_score(url)
        print(f"SSL risk: {ssl_risk}%")

        if model is not None:
            try:
                features, _ = extract_features_from_url(url)
                if features.shape[1] == model.n_features_in_:
                    probabilities = model.predict_proba(features)[0]
                    if hasattr(model, 'classes_'):
                        classes = list(model.classes_)
                        phishing_prob = probabilities[classes.index(1)] if 1 in classes else probabilities[0]
                    else:
                        phishing_prob = probabilities[1] if len(probabilities) > 1 else probabilities[0]
                    ml_risk = float(round(phishing_prob * 100, 2))
                    print(f"ML risk: {ml_risk}%")

                    final_risk = (ml_risk * 0.35) + (heuristic_risk * 0.35) + (domain_risk * 0.20) + (ssl_risk * 0.10)
                    final_risk = min(100.0, final_risk)
                    print(f"Final risk: {final_risk}%")
                    
                    domain_summary = get_domain_summary(url)
                    print(f"Domain info: {domain_summary}")
                    
                    ssl_summary = get_ssl_summary(url)
                    print(f"SSL info: {ssl_summary}")
                    
                    return final_risk
            except Exception as e:
                print(f"ML error: {e}")

        final_risk = (heuristic_risk * 0.5) + (domain_risk * 0.3) + (ssl_risk * 0.2)
        final_risk = min(100.0, final_risk)
        print(f"Final risk: {final_risk}%")
        return final_risk
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return heuristic_analysis(url)


def get_model_info():
    if model is None:
        return {"status": "Not loaded"}
    return {
        "status": "Loaded",
        "type": type(model).__name__,
        "features": model.n_features_in_,
        "classes": model.classes_.tolist() if hasattr(model, 'classes_') else "Unknown",
        "trees": model.n_estimators if hasattr(model, 'n_estimators') else "Unknown"
    }