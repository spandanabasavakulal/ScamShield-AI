
# ==========================================
# SCAMSHIELD AI - GEMINI-POWERED EXPLANATION AGENT
# ==========================================

import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ==========================================
# CONFIGURATION
# ==========================================

load_dotenv()

GEMINI_MODEL = "gemini-3.5-flash-lite"

MAX_RETRIES = 3
RETRY_DELAYS = [2, 4]


# ==========================================
# EXPLANATION AGENT
# ==========================================

def generate_explanation(
    message_result=None,
    url_results=None,
    impersonation_result=None,
    payment_result=None
):
    """
    Combines evidence from all detection agents.

    Risk assessment: Deterministic
    Natural-language explanation: Gemini
    Retry mechanism: Exponential backoff
    Fallback: Rule-based explanation
    """

    message_result = message_result or {}
    url_results = url_results or []
    impersonation_result = impersonation_result or {}
    payment_result = payment_result or {}

    evidence = []
    recommendations = []

    # ==========================================
    # 1. MESSAGE ANALYSIS AGENT
    # ==========================================

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

    # ==========================================
    # 2. URL INTELLIGENCE AGENT
    # ==========================================

    for url_result in url_results:

        risk_level = url_result.get("risk_level")
        url = url_result.get("url", "Unknown URL")

        if risk_level in ["High", "Medium"]:

            evidence.append(
                f"Suspicious URL detected: {url}"
            )

            evidence.extend(
                url_result.get("indicators", [])
            )

        reputation = url_result.get("reputation_status")

        if reputation == "known_phishing":

            evidence.append(
                f"URL found in the OpenPhish phishing feed: {url}"
            )

            recommendations.append(
                "Do not visit this URL."
            )

        elif reputation == "unknown":

            evidence.append(
                f"URL reputation could not be verified: {url}"
            )

        elif reputation == "not_found":

            evidence.append(
                f"URL was not found in the OpenPhish feed: {url}. "
                "This does not establish that the URL is safe."
            )

        elif reputation == "listed_unverified":

            evidence.append(
                f"URL is listed but not verified in reputation data: {url}"
            )

    # ==========================================
    # 3. IMPERSONATION DETECTION AGENT
    # ==========================================

    impersonation_score = impersonation_result.get(
        "risk_score", 0
    )

    if impersonation_score > 0:

        explanation = impersonation_result.get(
            "explanation", ""
        )

        evidence.append(
            "Impersonation-related indicators detected: "
            + explanation
        )

        recommendations.append(
            "Verify the sender using the organisation's official contact details."
        )

    # ==========================================
    # 4. PAYMENT RISK AGENT
    # ==========================================

    payment_score = payment_result.get("risk_score", 0)

    if payment_score > 0:

        explanation = payment_result.get(
            "explanation", ""
        )

        evidence.append(
            "Payment-related risk indicators detected: "
            + explanation
        )

        recommendations.append(
            "Never share OTPs, UPI PINs or passwords."
        )

    # ==========================================
    # 5. DETERMINISTIC RISK ASSESSMENT
    # ==========================================

    high_risk_detected = False
    medium_risk_detected = False

    # A phishing ML prediction is evidence, not
    # automatic proof of high overall risk.

    if prediction == "Phishing Email":
        medium_risk_detected = True

    # URL risk

    for result in url_results:

        if result.get("risk_level") == "High":
            high_risk_detected = True

        elif result.get("risk_level") == "Medium":
            medium_risk_detected = True

        if result.get("reputation_status") == "known_phishing":
            high_risk_detected = True

    # Impersonation risk

    if impersonation_result.get("risk_level") == "High":
        high_risk_detected = True

    elif impersonation_result.get("risk_level") == "Medium":
        medium_risk_detected = True

    # Payment risk

    if payment_result.get("risk_level") == "High":
        high_risk_detected = True

    elif payment_result.get("risk_level") == "Medium":
        medium_risk_detected = True

    # Final risk

    if high_risk_detected:
        overall_risk = "High"

    elif medium_risk_detected:
        overall_risk = "Medium"

    else:
        overall_risk = "Low"

    # ==========================================
    # 6. RECOMMENDATIONS
    # ==========================================

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

    # ==========================================
    # 7. GEMINI EXPLANATION GENERATION
    # ==========================================

    ai_explanation = None
    llm_status = "fallback"

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:

        client = None

        try:

            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(
                    timeout=20000
                )
            )

            prompt = f"""
You are the Explanation Agent of ScamShield AI,
a financial scam detection and risk assessment system.

Explain the analysis using ONLY the evidence provided below.

Overall risk level: {overall_risk}

Detection evidence:
{evidence}

Recommendations:
{recommendations}

Rules:
1. Explain why this risk level was assigned.
2. Use only the supplied evidence.
3. Do not invent URLs, brands, threats or indicators.
4. Do not claim a message is fraudulent without sufficient evidence.
5. Do not change the assigned risk level.
6. Explain that an unlisted URL is not necessarily safe.
7. Use clear, simple professional language.
8. Keep the explanation within 100 words.
"""

            # Retry temporary API failures

            for attempt in range(MAX_RETRIES):

                try:

                    print(
                        f"Gemini request: Attempt "
                        f"{attempt + 1}/{MAX_RETRIES}"
                    )

                    response = client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=prompt
                    )

                    ai_explanation = response.text

                    if ai_explanation and ai_explanation.strip():

                        llm_status = "success"

                        print(
                            "Gemini explanation generated successfully."
                        )

                        break

                    else:

                        ai_explanation = None

                        print(
                            "Gemini returned an empty response."
                        )

                        break

                except Exception as error:

                    error_message = str(error).upper()

                    temporary_errors = [
                        "503",
                        "UNAVAILABLE",
                        "429",
                        "RESOURCE_EXHAUSTED",
                        "500",
                        "INTERNAL",
                        "504",
                        "DEADLINE_EXCEEDED",
                        "TIMEOUT"
                    ]

                    is_temporary = any(
                        code in error_message
                        for code in temporary_errors
                    )

                    print(
                        f"Gemini attempt {attempt + 1} failed: {error}"
                    )

                    # Do not retry permanent errors

                    if not is_temporary:

                        print(
                            "Non-retryable Gemini error."
                        )

                        break

                    # Retry only if attempts remain

                    if attempt < MAX_RETRIES - 1:

                        delay = RETRY_DELAYS[attempt]

                        print(
                            f"Temporary API failure. "
                            f"Retrying in {delay} seconds..."
                        )

                        time.sleep(delay)

        except Exception as error:

            print(
                "Gemini client initialization failed:",
                error
            )

        finally:

            if client is not None:

                try:
                    client.close()

                except Exception:
                    pass

    else:

        print(
            "GEMINI_API_KEY not found. "
            "Using rule-based fallback."
        )

    # ==========================================
    # 8. DETERMINISTIC FALLBACK
    # ==========================================

    if not ai_explanation:

        llm_status = "fallback"

        if overall_risk == "High":

            ai_explanation = (
                "High risk detected because one or more detection "
                "agents identified strong indicators of suspicious "
                "activity. Review the evidence and verify the sender "
                "before taking action."
            )

        elif overall_risk == "Medium":

            ai_explanation = (
                "Medium risk detected because some suspicious "
                "patterns were identified. Independently verify "
                "the message and its requests before proceeding."
            )

        else:

            ai_explanation = (
                "Low risk detected because the available agents "
                "did not identify strong suspicious indicators. "
                "This does not guarantee that the message is safe."
            )

    # ==========================================
    # 9. FINAL OUTPUT
    # ==========================================

    return {
        "overall_risk": overall_risk,
        "evidence": evidence,
        "recommendations": recommendations,
        "ai_explanation": ai_explanation,
        "llm_status": llm_status
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

    print("\nSCAMSHIELD AI - GEMINI EXPLANATION AGENT")
    print("=" * 55)

    print("Overall Risk:", result["overall_risk"])

    print("\nEvidence:")

    for item in result["evidence"]:
        print("-", item)

    print("\nAI Explanation:")
    print(result["ai_explanation"])

    print("\nLLM Status:", result["llm_status"])

    print("\nRecommendations:")

    for item in result["recommendations"]:
        print("-", item)

    print("=" * 55)
