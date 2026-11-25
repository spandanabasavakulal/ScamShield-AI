
import streamlit as st
from workflow.graph import run_scamshield

st.set_page_config(
    page_title="ScamShield AI",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- PAGE HEADER ----------------

st.title("🛡️ ScamShield AI")

st.subheader(
    "Agentic AI Framework for Intelligent "
    "Financial Scam Detection and Risk Assessment"
)

st.write(
    "Analyse suspicious emails, SMS messages and "
    "payment-related communications using AI."
)

st.divider()

# ---------------- USER INPUT ----------------

message = st.text_area(
    "Enter a suspicious message:",
    placeholder="Paste your email, SMS or payment message here...",
    height=200
)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if st.button("Analyse Message", type="primary"):

    if message.strip():

        try:
            with st.spinner(
                "Running ScamShield AI agents... Please wait."
            ):
                result = run_scamshield(message)

            st.session_state.analysis_result = result

        except Exception as e:
            st.error("An error occurred during analysis.")
            st.exception(e)

    else:
        st.warning("Please enter a message.")

# ---------------- DISPLAY RESULTS ----------------

result = st.session_state.analysis_result

if result:

    st.divider()
    st.header("Analysis Results")

    message_result = result.get("message_result", {})
    url_results = result.get("url_results", [])
    impersonation = result.get("impersonation_result", {})
    payment = result.get("payment_result", {})
    explanation = result.get("explanation_result", {})

    overall_risk = result.get(
        "overall_risk",
        explanation.get("overall_risk", "Unknown")
    )

    # ---------------- OVERALL RISK ----------------

    st.subheader("Overall Risk Assessment")

    if overall_risk == "High":
        st.error("🚨 HIGH RISK - Potential Scam Detected")

    elif overall_risk == "Medium":
        st.warning("⚠️ MEDIUM RISK - Suspicious Indicators Found")

    elif overall_risk == "Low":
        st.success("LOW RISK - Fewer Suspicious Indicators Detected")

    else:
        st.info(f"Risk Level: {overall_risk}")

    # ---------------- MESSAGE ANALYSIS ----------------

    with st.expander("1. Message Analysis Agent", expanded=True):

        prediction = message_result.get("prediction", "Unknown")

        st.write("**Prediction:**", prediction)
        st.write(
            "**Analysis:**",
            message_result.get("message", "No explanation available.")
        )

    # ---------------- URL INTELLIGENCE ----------------

    with st.expander("2. URL Intelligence Agent", expanded=True):

        if url_results:

            for item in url_results:

                st.write("**URL:**", item.get("url", "Unknown"))
                st.write("**Domain:**", item.get("domain", "Unknown"))
                st.write("**Risk Score:**", item.get("risk_score", 0))
                st.write("**Risk Level:**", item.get("risk_level", "Unknown"))
                st.write(
                    "**Reputation:**",
                    item.get("reputation_status", "Unknown")
                )

                st.write("**Indicators:**")

                indicators = item.get("indicators", [])

                if indicators:
                    for indicator in indicators:
                        st.write(f"- {indicator}")
                else:
                    st.write("No heuristic indicators detected.")

                st.caption(
                    item.get("reputation_message", "")
                )

                st.divider()

        else:
            st.info("No URLs detected in the submitted message.")

    # ---------------- IMPERSONATION DETECTION ----------------

    with st.expander("3. Impersonation Detection Agent", expanded=True):

        st.write(
            "**Risk Score:**",
            impersonation.get("risk_score", 0)
        )

        st.write(
            "**Risk Level:**",
            impersonation.get("risk_level", "Unknown")
        )

        st.write(
            "**Brand Mentions:**",
            ", ".join(impersonation.get("brand_mentions", [])) or "None"
        )

        st.write(
            "**Authority Mentions:**",
            ", ".join(impersonation.get("authority_mentions", [])) or "None"
        )

        st.write(
            "**Urgency Indicators:**",
            ", ".join(impersonation.get("urgency_indicators", [])) or "None"
        )

        st.write(
            "**Sensitive Requests:**",
            ", ".join(impersonation.get("sensitive_requests", [])) or "None"
        )

        st.write(
            "**Explanation:**",
            impersonation.get("explanation", "No explanation available.")
        )

    # ---------------- PAYMENT RISK ----------------

    with st.expander("4. Payment Risk Assessment Agent", expanded=True):

        st.write(
            "**Risk Score:**",
            payment.get("risk_score", 0)
        )

        st.write(
            "**Risk Level:**",
            payment.get("risk_level", "Unknown")
        )

        st.write(
            "**Payment Indicators:**",
            ", ".join(payment.get("payment_indicators", [])) or "None"
        )

        st.write(
            "**Urgency Indicators:**",
            ", ".join(payment.get("urgency_indicators", [])) or "None"
        )

        st.write(
            "**Sensitive Requests:**",
            ", ".join(payment.get("sensitive_requests", [])) or "None"
        )

        st.write(
            "**Alternative Payment Methods:**",
            ", ".join(payment.get("alternative_payment_methods", [])) or "None"
        )

        st.write(
            "**Payment Link Indicators:**",
            ", ".join(payment.get("payment_link_indicators", [])) or "None"
        )

        st.write(
            "**Explanation:**",
            payment.get("explanation", "No explanation available.")
        )

    # ---------------- GEMINI EXPLANATION ----------------

    with st.expander("5. AI Explanation Agent", expanded=True):

        st.write("**Gemini Status:**", explanation.get("llm_status", "Unknown"))

        st.markdown(
            explanation.get(
                "ai_explanation",
                "AI explanation is not available."
            )
        )

    # ---------------- SECURITY RECOMMENDATIONS ----------------

    st.subheader("Security Recommendations")

    recommendations = explanation.get("recommendations", [])

    if recommendations:
        for recommendation in recommendations:
            st.write(f"- {recommendation}")
    else:
        st.info("No recommendations available.")

    # ---------------- EVIDENCE SUMMARY ----------------

    with st.expander("Detailed Evidence Summary"):

        evidence = explanation.get("evidence", [])

        if evidence:
            for item in evidence:
                st.write(f"- {item}")
        else:
            st.write("No additional evidence available.")

    # ---------------- DISCLAIMER ----------------

    st.divider()

    st.caption(
        "ScamShield AI provides automated risk screening. "
        "A Low risk result does not guarantee that a message is safe."
    )
