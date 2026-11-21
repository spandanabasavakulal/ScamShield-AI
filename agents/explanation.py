
# ==========================================
# SCAMSHIELD AI - EXPLANATION AGENT
# ==========================================

def generate_explanation(
    message_result=None,
    url_results=None,
    impersonation_result=None,
    payment_result=None
):

    url_results = url_results or []

    evidence = []
    recommendations = []

    # 1. Message Analysis Agent
    if message_result:

        prediction = message_result.get("prediction")

        if prediction == "Phishing Email":
            evidence.append(
                "Machine learning model detected phishing patterns."
            )

            recommendations.append(
                "Avoid clicking links or responding to the message."
            )

        elif prediction == "Safe Email":
            evidence.append(
                "Machine learning model did not detect phishing patterns."
            )

    # 2. URL Intelligence Agent
    for url_result in url_results:

        risk_level = url_result.get("risk_level")

        if risk_level in ["High", "Medium"]:

            evidence.append(
                f"Suspicious URL detected: "
                f"{url_result.get('url')}"
            )

            evidence.extend(
                url_result.get("indicators", [])
            )

        reputation = url_result.get("reputation_status")

        if reputation == "known_phishing":

            evidence.append(
                "URL was found in the OpenPhish phishing feed."
            )

            recommendations.append(
                "Do not visit this URL."
            )

        elif reputation == "listed_unverified":

            evidence.append(
                "URL is listed but not verified in reputation data."
            )

        elif reputation == "unknown":

            evidence.append(
                "URL reputation could not be verified."
            )

    # 3. Impersonation Detection Agent
    if impersonation_result:

        impersonation_score = impersonation_result.get(
            "risk_score", 0
        )

        if impersonation_score > 0:

            evidence.append(
                "Impersonation-related indicators detected: "
                + impersonation_result.get("explanation", "")
            )

            recommendations.append(
                "Verify the sender using the organisation's official contact details."
            )

    # 4. Payment Risk Agent
    if payment_result:

        payment_score = payment_result.get("risk_score", 0)

        if payment_score > 0:

            evidence.append(
                "Payment-related risk indicators detected: "
                + payment_result.get("explanation", "")
            )

            recommendations.append(
                "Do not share OTPs, UPI PINs or passwords."
            )

    # 5. Overall risk assessment
    high_risk_detected = False
    medium_risk_detected = False

    if message_result:
        if message_result.get("prediction") == "Phishing Email":
            high_risk_detected = True

    for result in url_results:

        if result.get("risk_level") == "High":
            high_risk_detected = True

        elif result.get("risk_level") == "Medium":
            medium_risk_detected = True

        if result.get("reputation_status") == "known_phishing":
            high_risk_detected = True

    if impersonation_result:
        if impersonation_result.get("risk_level") == "High":
            high_risk_detected = True

        elif impersonation_result.get("risk_level") == "Medium":
            medium_risk_detected = True

    if payment_result:
        if payment_result.get("risk_level") == "High":
            high_risk_detected = True

        elif payment_result.get("risk_level") == "Medium":
            medium_risk_detected = True

    if high_risk_detected:
        overall_risk = "High"

    elif medium_risk_detected:
        overall_risk = "Medium"

    else:
        overall_risk = "Low"

    # 6. Recommendations
    if overall_risk == "High":

        recommendations.append(
            "Treat this message as potentially dangerous."
        )

    elif overall_risk == "Medium":

        recommendations.append(
            "Exercise caution and independently verify the request."
        )

    else:

        recommendations.append(
            "No strong risk indicators were detected. "
            "Remain cautious."
        )

    if not evidence:

        evidence.append(
            "No suspicious indicators were detected by the available agents."
        )

    # Remove duplicate recommendations
    recommendations = list(dict.fromkeys(recommendations))

    return {
        "overall_risk": overall_risk,
        "evidence": evidence,
        "recommendations": recommendations
    }


# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    sample_message_result = {
        "prediction": "Phishing Email"
    }

    sample_url_results = [
        {
            "url": "https://paypal-login.example/verify",
            "risk_level": "High",
            "indicators": [
                "Suspicious hostname keywords",
                "Possible brand impersonation"
            ],
            "reputation_status": "not_found"
        }
    ]

    sample_impersonation_result = {
        "risk_score": 60,
        "risk_level": "High",
        "explanation": "SBI impersonation and OTP request detected."
    }

    sample_payment_result = {
        "risk_score": 65,
        "risk_level": "High",
        "explanation": "Urgent payment and sensitive information request."
    }

    result = generate_explanation(
        message_result=sample_message_result,
        url_results=sample_url_results,
        impersonation_result=sample_impersonation_result,
        payment_result=sample_payment_result
    )

    print("\nSCAMSHIELD AI - EXPLANATION AGENT")
    print("=" * 50)

    print("Overall Risk:", result["overall_risk"])

    print("\nEvidence:")

    for item in result["evidence"]:
        print("-", item)

    print("\nRecommendations:")

    for item in result["recommendations"]:
        print("-", item)

    print("=" * 50)
