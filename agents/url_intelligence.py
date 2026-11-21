
import re
import ipaddress
import requests
import tldextract

from urllib.parse import urlparse
from functools import lru_cache


# ==========================================
# CONFIGURATION
# ==========================================

OPENPHISH_FEED_URL = "https://openphish.com/feed.txt"

SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
    "cutt.ly",
    "rebrand.ly"
}

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "update",
    "account", "bank", "password",
    "wallet", "payment", "confirm"
]

BRAND_DOMAINS = {
    "paypal": "paypal.com",
    "google": "google.com",
    "amazon": "amazon.com",
    "microsoft": "microsoft.com",
    "facebook": "facebook.com"
}


# ==========================================
# 1. URL EXTRACTION
# ==========================================

def extract_urls(message):

    if not isinstance(message, str) or not message.strip():
        return []

    pattern = r"""(?i)\b(?:(?:https?://|www\.)[^\s<>"']+|(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s<>"']*)?)"""

    urls = re.findall(pattern, message)

    cleaned_urls = []

    for url in urls:

        url = url.rstrip(".,!?;:)]}")

        if url:
            cleaned_urls.append(url)

    return list(dict.fromkeys(cleaned_urls))


# ==========================================
# 2. URL HEURISTIC ANALYSIS
# ==========================================

def analyze_url(url):

    normalized_url = url.strip()

    if normalized_url.startswith("www."):
        normalized_url = "http://" + normalized_url

    elif not re.match(r"(?i)^https?://", normalized_url):
        normalized_url = "http://" + normalized_url

    try:
        parsed = urlparse(normalized_url)
        domain = parsed.hostname

        # Validate hostname
        if not domain:
            raise ValueError("Missing hostname")

        domain = domain.lower().rstrip(".")

        # Validate port if supplied
        _ = parsed.port

    except ValueError:

        return {
            "url": url,
            "domain": None,
            "risk_score": 0,
            "risk_level": "Invalid URL",
            "indicators": []
        }

    indicators = []
    risk_score = 0

    def add_indicator(description, score):

        nonlocal risk_score

        indicators.append(description)
        risk_score += score

    # 1. IP address detection
    try:

        ipaddress.ip_address(domain)

        add_indicator(
            "Uses an IP address instead of a domain",
            30
        )

    except ValueError:
        pass

    # 2. URL shortener detection
    if domain in SHORTENERS:

        add_indicator(
            "Uses a URL shortening service",
            20
        )

    # 3. Suspicious hostname keywords
    matched_keywords = [
        word for word in SUSPICIOUS_KEYWORDS
        if word in domain
    ]

    if matched_keywords:

        add_indicator(
            "Contains suspicious hostname keywords: "
            + ", ".join(matched_keywords),
            15
        )

    # 4. Multiple subdomains
    extracted = tldextract.extract(domain)

    subdomains = [
        part for part in extracted.subdomain.split(".")
        if part
    ]

    if len(subdomains) >= 3:

        add_indicator(
            "Contains multiple subdomains",
            15
        )

    # 5. HTTP instead of HTTPS
    if parsed.scheme.lower() == "http":

        add_indicator(
            "Uses HTTP instead of HTTPS",
            10
        )

    # 6. Excessive URL length
    if len(url) > 100:

        add_indicator(
            "URL has an unusually long length",
            10
        )

    # 7. @ symbol detection
    if "@" in parsed.netloc:

        add_indicator(
            "Contains an @ symbol in the URL authority",
            20
        )

    # 8. Brand impersonation detection
    for brand, official_domain in BRAND_DOMAINS.items():

        hostname_is_official = (
            domain == official_domain
            or domain.endswith("." + official_domain)
        )

        if brand in domain and not hostname_is_official:

            add_indicator(
                f"Brand name '{brand}' appears outside "
                "its official domain",
                25
            )

    # Risk classification
    if risk_score >= 40:
        risk_level = "High"

    elif risk_score >= 20:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    return {
        "url": url,
        "domain": domain,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "indicators": indicators
    }


# ==========================================
# 3. OPENPHISH FEED DOWNLOAD
# ==========================================

@lru_cache(maxsize=1)
def download_openphish_feed():

    response = requests.get(
        OPENPHISH_FEED_URL,
        timeout=20
    )

    response.raise_for_status()

    urls = {
        line.strip()
        for line in response.text.splitlines()
        if line.strip().startswith(("http://", "https://"))
    }

    return frozenset(urls)


# ==========================================
# 4. OPENPHISH REPUTATION CHECK
# ==========================================

def check_openphish(url):

    try:

        known_urls = download_openphish_feed()

        normalized_url = url.strip().rstrip("/")

        matching_url = next(
            (
                item for item in known_urls
                if item.rstrip("/") == normalized_url
            ),
            None
        )

        if matching_url:

            return {
                "status": "known_phishing",
                "message": "URL found in OpenPhish phishing feed."
            }

        return {
            "status": "not_found",
            "message": "URL not found in OpenPhish feed."
        }

    except requests.exceptions.RequestException:

        return {
            "status": "unknown",
            "message": "Unable to connect to OpenPhish."
        }

    except Exception:

        return {
            "status": "unknown",
            "message": "Unexpected error during reputation checking."
        }


# ==========================================
# 5. COMPLETE URL ANALYSIS
# ==========================================

def analyze_message_urls(message):

    urls = extract_urls(message)

    results = []

    for url in urls:

        heuristic_result = analyze_url(url)

        if heuristic_result["risk_level"] == "Invalid URL":

            reputation_result = {
                "status": "unknown",
                "message": "Invalid URL; reputation check skipped."
            }

        else:

            reputation_result = check_openphish(url)

        results.append({

            "url": url,

            "domain": heuristic_result["domain"],

            "risk_score": heuristic_result["risk_score"],

            "risk_level": heuristic_result["risk_level"],

            "indicators": heuristic_result["indicators"],

            "reputation_status": reputation_result["status"],

            "reputation_message": reputation_result["message"]

        })

    return results


# ==========================================
# 6. TESTING
# ==========================================

if __name__ == "__main__":

    test_message = """
    Your bank account is blocked!

    Verify immediately:
    https://secure-bank.example/login

    Another suspicious link:
    https://bit.ly/example

    Official website:
    https://google.com
    """

    print("\nSCAMSHIELD AI - URL INTELLIGENCE AGENT")

    print("=" * 60)

    results = analyze_message_urls(test_message)

    if not results:

        print("No URLs found.")

    for result in results:

        print("\nURL:", result["url"])

        print("Domain:", result["domain"])

        print("Heuristic Risk Score:", result["risk_score"])

        print("Heuristic Risk Level:", result["risk_level"])

        print("Indicators:")

        if result["indicators"]:

            for indicator in result["indicators"]:
                print("-", indicator)

        else:

            print("- No suspicious indicators found")

        print("\nOpenPhish Reputation:")
        print("Status:", result["reputation_status"])
        print("Details:", result["reputation_message"])

        print("-" * 60)
