
import streamlit as st
from models.predict import predict_email

st.set_page_config(
    page_title="ScamShield AI",
    page_icon="🛡️",
    layout="wide"
)

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

message = st.text_area(
    "Enter a suspicious message:",
    placeholder="Paste your email, SMS or payment message here...",
    height=200
)

if st.button("Analyse Message", type="primary"):

    if message.strip():

        with st.spinner("Analysing your message..."):

            result = predict_email(message)

        st.subheader("Analysis Results")

        if result["prediction"] == "Phishing Email":

            st.error("⚠️ Potential Phishing Detected")

        else:

            st.success("No phishing pattern detected")

        st.write("**Prediction:**", result["prediction"])
        st.write("**Analysis:**", result["message"])

        st.caption(
            "This is an automated screening result, not a guarantee "
            "that the message is safe or fraudulent."
        )

    else:

        st.warning("Please enter a message.")
