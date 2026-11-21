
import re


# ==========================================
# PAYMENT RISK DETECTION PATTERNS
# ==========================================

PAYMENT_KEYWORDS = [
    "upi", "payment", "transfer money",
    "send money", "bank transfer",
    "transaction", "refund", "cashback",
    "collect request", "payment request"
]

URGENT_PAYMENT_TERMS = [
    "pay immediately",
    "transfer immediately",
    "send money now",
    "urgent payment",
    "limited time offer",
    "pay within 24 hours",
    "account will be blocked",
    "last chance to pay"
]

SENSITIVE_PAYMENT_TERMS = [
    "share your otp",
    "send otp",
    "enter your otp",
    "share upi pin",
    "enter your upi pin",
    "share your pin",
    "share your password",
    "enter your password"
]

ALTERNATIVE_PAYMENT_METHODS = [
    "gift card",
    "google play card",
    "itunes card",
    "bitcoin",
    "cryptocurrency",
    "crypto wallet",
    "send bitcoin"
]

PAYMENT_LINK_KEYWORDS = [
    "payment link",
    "pay here",
    "click to pay",
    "claim refund",
    "verify bank account"
]


# ==========================================
# HELPER FUNCTION
# ==========================================

def find_matches(message, keywords):

    text = message.lower()

    return [
        keyword for keyword in keywords
        if keyword in text
    ]


# ==========================================
# PAYMENT RISK ANALYSIS
# ==========================================

def analyze_payment_risk(message):

    if not isinstance(message, str) or not message.strip():

        return {
            "risk_score": 0,
            "risk_level": "Invalid Input",
            "payment_indicators": [],
            "urgency_indicators": [],
            "sensitive_requests": [],
            "alternative_payment_methods": [],
            "payment_link_indicators": [],
            "explanation": "Please enter a valid message."
        }

    payment_indicators = find_matches(
        message, PAYMENT_KEYWORDS
    )

    urgency_indicators = find_matches(
        message, URGENT_PAYMENT_TERMS
    )

    sensitive_requests = find_matches(
        message, SENSITIVE_PAYMENT_TERMS
    )

    alternative_methods = find_matches(
        message, ALTERNATIVE_PAYMENT_METHODS
    )

    payment_link_indicators = find_matches(
        message, PAYMENT_LINK_KEYWORDS
    )

    risk_score = 0
    explanations = []

    # 1. Payment-related language
    if payment_indicators:
        risk_score += 10
        explanations.append(
            "Payment-related language detected"
        )

    # 2. Urgent payment demands
    if urgency_indicators:
        risk_score += 20
        explanations.append(
            "Urgent payment demand detected"
        )

    # 3. Sensitive information requests
    if sensitive_requests:
        risk_score += 35
        explanations.append(
            "Sensitive banking information requested"
        )

    # 4. Alternative payment methods
    if alternative_methods:
        risk_score += 25
        explanations.append(
            "Potentially suspicious alternative payment method"
        )

    # 5. Payment-related links
    if payment_link_indicators:
        risk_score += 15
        explanations.append(
            "Payment or refund link language detected"
        )

    # Risk classification
    if risk_score >= 50:
        risk_level = "High"

    elif risk_score >= 25:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    if not explanations:
        explanations.append(
            "No payment-related risk indicators detected"
        )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "payment_indicators": payment_indicators,
        "urgency_indicators": urgency_indicators,
        "sensitive_requests": sensitive_requests,
        "alternative_payment_methods": alternative_methods,
        "payment_link_indicators": payment_link_indicators,
        "explanation": "; ".join(explanations)
    }


# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    test_messages = [

        """
        Your bank account will be blocked.
        Transfer money immediately to avoid suspension.
        """,

        """
        Your UPI refund is pending.
        Click to pay and claim your refund.
        """,

        """
        Congratulations! You won a prize.
        Share your OTP and UPI PIN to receive money.
        """,

        """
        Your order has been successfully delivered.
        Thank you for shopping with us.
        """,

        """
        Send bitcoin to this crypto wallet
        to receive your investment returns.
        """
    ]

    for index, message in enumerate(test_messages, start=1):

        result = analyze_payment_risk(message)

        print("\nPAYMENT RISK TEST:", index)
        print("=" * 55)

        print("Risk Score:", result["risk_score"])
        print("Risk Level:", result["risk_level"])

        print("Payment Indicators:",
              result["payment_indicators"])

        print("Urgency Indicators:",
              result["urgency_indicators"])

        print("Sensitive Requests:",
              result["sensitive_requests"])

        print("Alternative Payment Methods:",
              result["alternative_payment_methods"])

        print("Payment Link Indicators:",
              result["payment_link_indicators"])

        print("Explanation:", result["explanation"])

        print("=" * 55)
