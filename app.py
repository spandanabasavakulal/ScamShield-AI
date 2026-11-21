
import streamlit as st

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

st.write("Welcome to ScamShield AI!")

message = st.text_area(
    "Enter a suspicious message:",
    placeholder="Paste your email, SMS or payment message here..."
)

if st.button("Analyse Message"):
    if message.strip():
        st.info("Application setup successful!")
    else:
        st.warning("Please enter a message.")
