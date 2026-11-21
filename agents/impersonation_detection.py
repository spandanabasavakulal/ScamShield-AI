
import re


# Organisations and brands commonly impersonated
TRUSTED_BRANDS = {
    "paypal": ["paypal"],
    "google": ["google"],
    "amazon": ["amazon"],
    "microsoft": ["microsoft"],
    "facebook": ["facebook"],
    "sbi": ["sbi", "state bank of india"],
    "hdfc": ["hdfc"],
    "icici": ["icici"],
    "axis bank": ["axis bank"],
    "phonepe": ["phonepe"],
    "paytm": ["paytm"],
    "google pay": ["google pay", "gpay"],
}

AUTHORITY_TERMS = [
    "government",
    "police",
    "income tax department",
    "tax department",
    "rbi",
    "reserve bank of india",
    "court",
    "cyber crime department",
]

URGENCY_TERMS = [
    "immediately",
    "urgent",
    "account blocked",
    "account suspended",
    "verify now",
    "act now",
    "within 24 hours",
    "last warning",
]

SENSITIVE_REQUESTS = [
    "share your otp",
    "enter your otp",
    "send otp",
    "share password",
    "enter password",
    "share your pin",
    "enter your pin",
    "send money",
    "transfer money",
    "pay immediately",
]


def detect_brand_mentions(message):

    text = message.lower()
    detected = []

    for brand, keywords in TRUSTED_BRANDS.items():

        for keyword in keywords:

            if re.search(
                r"\b" + re.escape(keyword) + r"\b",
                text
            ):

                detected.append(brand)
                break

    return detected


def detect_authority_impersonation(message):

    text = message.lower()

    return [
        term for term in AUTHORITY_TERMS
        if re.search(r"\b" + re.escape(term) + r"\b", text)
    ]


def detect_urgency(message):

    text = message.lower()

    return [
        term for term in URGENCY_TERMS
        if term in text
    ]


def detect_sensitive_requests(message):

    text = message.lower()

    return [
        term for term in SENSITIVE_REQUESTS
        if term in text
    ]


def analyze_impersonation(message):

    if not isinstance(message, str) or not message.strip():

        return {
            "risk_score": 0,
            "risk_level": "Invalid Input",
            "brand_mentions": [],
            "authority_mentions": [],
            "urgency_indicators": [],
            "sensitive_requests": [],
            "explanation": "Please enter a valid message."
        }

    brand_mentions = detect_brand_mentions(message)

    authority_mentions = detect_authority_impersonation(message)

    urgency_indicators = detect_urgency(message)

    sensitive_requests = detect_sensitive_requests(message)

    risk_score = 0
    indicators = []

    if brand_mentions:
        risk_score += 15
        indicators.append(
            "Trusted brand references: "
            + ", ".join(brand_mentions)
        )

    if authority_mentions:
        risk_score += 20
        indicators.append(
            "Authority references: "
            + ", ".join(authority_mentions)
        )

    if urgency_indicators:
        risk_score += 15
        indicators.append(
            "Urgency indicators: "
            + ", ".join(urgency_indicators)
        )

    if sensitive_requests:
        risk_score += 30
        indicators.append(
            "Sensitive information or payment requests: "
            + ", ".join(sensitive_requests)
        )

    if risk_score >= 40:
        risk_level = "High"

    elif risk_score >= 20:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    if indicators:
        explanation = "; ".join(indicators)
    else:
        explanation = "No impersonation-related indicators detected."

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "brand_mentions": brand_mentions,
        "authority_mentions": authority_mentions,
        "urgency_indicators": urgency_indicators,
        "sensitive_requests": sensitive_requests,
        "explanation": explanation
    }


# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    test_messages = [

        """
        Your SBI account has been blocked.
        Verify now and share your OTP immediately.
        """,

        """
        Congratulations! Your Amazon order has been delivered.
        Thank you for shopping with us.
        """,

        """
        This is a message from the police department.
        Pay immediately or face legal action.
        """,

        """
        Dear student, your examination results are published.
        Please visit the university website.
        """
    ]

    for index, message in enumerate(test_messages, start=1):

        result = analyze_impersonation(message)

        print("\nTEST CASE:", index)
        print("=" * 50)

        print("Risk Score:", result["risk_score"])
        print("Risk Level:", result["risk_level"])

        print("Brand Mentions:", result["brand_mentions"])
        print("Authority Mentions:", result["authority_mentions"])
        print("Urgency:", result["urgency_indicators"])
        print("Sensitive Requests:", result["sensitive_requests"])

        print("Explanation:", result["explanation"])
        print("=" * 50)
