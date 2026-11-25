
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import json
from pathlib import Path
from datetime import datetime

from workflow.graph import run_scamshield


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ScamShield AI | Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "scamshield_history.db"

# Dataset metrics from the completed training experiment
TOTAL_RECORDS = 17521
SAFE_RECORDS = 10978
PHISHING_RECORDS = 6543

MODEL_METRICS = {
    "Logistic Regression": {
        "Accuracy": 97.95,
        "Precision": 96.82,
        "Recall": 97.71,
        "F1 Score": 97.26
    },
    "Multinomial Naive Bayes": {
        "Accuracy": 96.92,
        "Precision": 97.02,
        "Recall": 94.65,
        "F1 Score": 95.82
    },
    "Linear SVM": {
        "Accuracy": 98.12,
        "Precision": 97.41,
        "Recall": 97.56,
        "F1 Score": 97.48
    }
}


# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown("""
<style>
/* Fix metric labels */
[data-testid="stMetricLabel"] {
    color: #1E293B !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* Keep metric values clearly visible */
[data-testid="stMetricValue"] {
    color: #2563EB !important;
    font-weight: 700 !important;
}

/* Metric card styling */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DCE3ED !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE
# =========================================================

def initialize_database():

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                message_preview TEXT,
                overall_risk TEXT,
                prediction TEXT,
                url_count INTEGER,
                gemini_status TEXT
            )
        """)


def save_analysis(message, result):

    explanation = result.get("explanation_result", {})
    message_result = result.get("message_result", {})
    url_results = result.get("url_results", [])

    record = (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        message[:120],
        result.get(
            "overall_risk",
            explanation.get("overall_risk", "Unknown")
        ),
        message_result.get("prediction", "Unknown"),
        len(url_results),
        explanation.get("llm_status", "Unknown")
    )

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("""
            INSERT INTO analysis_history
            (timestamp, message_preview, overall_risk,
             prediction, url_count, gemini_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, record)


def get_history():

    with sqlite3.connect(DB_PATH) as conn:

        return pd.read_sql_query(
            "SELECT * FROM analysis_history ORDER BY id DESC",
            conn
        )


initialize_database()


# =========================================================
# DATASET LOADING
# =========================================================

def find_dataset():

    possible_files = [
        BASE_DIR / "data" / "processed" / "cleaned_phishing_emails.csv",
        BASE_DIR / "data" / "processed" / "phishing_emails_cleaned.csv",
        BASE_DIR / "data" / "processed" / "cleaned_data.csv",
        BASE_DIR / "data" / "processed" / "processed_data.csv"
    ]

    for file in possible_files:

        if file.exists():
            return file

    # Search for a CSV containing the expected dataset columns
    for file in (BASE_DIR / "data").rglob("*.csv"):

        try:
            columns = pd.read_csv(file, nrows=0).columns.tolist()

            if "Email Text" in columns and "Email Type" in columns:
                return file

        except Exception:
            continue

    return None


@st.cache_data
def load_dataset():

    dataset_path = find_dataset()

    if dataset_path is None:
        return None

    try:
        return pd.read_csv(dataset_path)

    except Exception:
        return None


dataset = load_dataset()


# =========================================================
# SESSION STATE
# =========================================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "analysis_message" not in st.session_state:
    st.session_state.analysis_message = ""


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:

    st.title("🛡️ ScamShield AI")

    st.caption("Financial Threat Intelligence Platform")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Dataset Analytics",
            "Model Performance",
            "Scam Analysis",
            "Analysis History"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### System Information")

    st.write("**ML Model:** Linear SVM")
    st.write("**Orchestration:** LangGraph")
    st.write("**LLM:** Gemini")
    st.write("**Storage:** SQLite")

    st.divider()

    st.caption("ScamShield AI | Academic Project")


# =========================================================
# COMMON HEADER
# =========================================================

st.title("🛡️ ScamShield AI")

st.caption(
    "Agentic AI Framework for Intelligent Financial Scam "
    "Detection and Risk Assessment"
)

st.markdown(
    "Analyse suspicious emails, SMS messages and "
    "payment-related communications using a multi-agent AI framework."
)

st.divider()


# =========================================================
# PAGE 1: OVERVIEW
# =========================================================

if page == "Overview":

    st.header("Security Dashboard")

    history = get_history()

    total_analyses = len(history)

    high_risk = (
        len(history[history["overall_risk"] == "High"])
        if total_analyses else 0
    )

    medium_risk = (
        len(history[history["overall_risk"] == "Medium"])
        if total_analyses else 0
    )

    low_risk = (
        len(history[history["overall_risk"] == "Low"])
        if total_analyses else 0
    )

    st.subheader("Dataset & Model Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Dataset Records", f"{TOTAL_RECORDS:,}")
    c2.metric("Safe Emails", f"{SAFE_RECORDS:,}")
    c3.metric("Phishing Emails", f"{PHISHING_RECORDS:,}")
    c4.metric("Best Model Accuracy", "98.12%")

    st.divider()

    st.subheader("Live Analysis Statistics")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Analyses", total_analyses)
    c2.metric("High Risk", high_risk)
    c3.metric("Medium Risk", medium_risk)
    c4.metric("Low Risk", low_risk)

    st.caption(
        "Analysis statistics are calculated from messages "
        "analysed through this dashboard and stored in SQLite."
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("Dataset Class Distribution")

        class_df = pd.DataFrame({
            "Category": ["Safe Email", "Phishing Email"],
            "Records": [SAFE_RECORDS, PHISHING_RECORDS]
        })

        fig = px.pie(
            class_df,
            names="Category",
            values="Records",
            hole=0.55,
            color="Category",
            color_discrete_map={
                "Safe Email": "#22c55e",
                "Phishing Email": "#ef4444"
            }
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1120",
            plot_bgcolor="#0b1120",
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        st.subheader("Model Accuracy Comparison")

        accuracy_df = pd.DataFrame({
            "Model": list(MODEL_METRICS.keys()),
            "Accuracy": [
                values["Accuracy"]
                for values in MODEL_METRICS.values()
            ]
        })

        fig = px.bar(
            accuracy_df,
            x="Model",
            y="Accuracy",
            text="Accuracy",
            color="Accuracy",
            color_continuous_scale="Blues"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1120",
            plot_bgcolor="#0b1120",
            yaxis_range=[90, 100],
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Agentic Detection Architecture")

    agent_cols = st.columns(5)

    agents = [
        "Message Analysis",
        "URL Intelligence",
        "Impersonation Detection",
        "Payment Risk",
        "AI Explanation"
    ]

    for col, agent in zip(agent_cols, agents):

        with col:
            st.info(agent)

    st.caption(
        "LangGraph orchestrates the five agents in a sequential "
        "workflow to generate an overall risk assessment."
    )


# =========================================================
# PAGE 2: DATASET ANALYTICS
# =========================================================

elif page == "Dataset Analytics":

    st.header("Dataset Analytics")

    st.write(
        "Exploratory analysis of the cleaned phishing email dataset."
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Records", f"{TOTAL_RECORDS:,}")
    c2.metric("Safe Records", f"{SAFE_RECORDS:,}")
    c3.metric("Phishing Records", f"{PHISHING_RECORDS:,}")

    st.divider()

    class_df = pd.DataFrame({
        "Email Type": ["Safe Email", "Phishing Email"],
        "Count": [SAFE_RECORDS, PHISHING_RECORDS]
    })

    left, right = st.columns(2)

    with left:

        st.subheader("Class Distribution")

        fig = px.bar(
            class_df,
            x="Email Type",
            y="Count",
            color="Email Type",
            text="Count",
            color_discrete_map={
                "Safe Email": "#22c55e",
                "Phishing Email": "#ef4444"
            }
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1120",
            plot_bgcolor="#0b1120"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        st.subheader("Safe vs Phishing Ratio")

        fig = px.pie(
            class_df,
            names="Email Type",
            values="Count",
            hole=0.5,
            color="Email Type",
            color_discrete_map={
                "Safe Email": "#22c55e",
                "Phishing Email": "#ef4444"
            }
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1120",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Dataset Visualizations")

    eda_dir = BASE_DIR / "assets" / "eda"

    image_files = [
        ("Class Distribution", "class_distribution.png"),
        ("Email Length Distribution", "email_length.png"),
        ("Phishing Word Cloud", "phishing_wordcloud.png"),
        ("Safe Email Word Cloud", "safe_wordcloud.png")
    ]

    found_images = False

    for title, filename in image_files:

        image_path = eda_dir / filename

        if image_path.exists():
            found_images = True

    if found_images:

        for i in range(0, len(image_files), 2):

            col1, col2 = st.columns(2)

            for col, item in zip(
                [col1, col2],
                image_files[i:i + 2]
            ):

                title, filename = item
                image_path = eda_dir / filename

                with col:

                    if image_path.exists():

                        st.markdown(f"**{title}**")
                        st.image(
                            str(image_path),
                            use_container_width=True
                        )

    else:

        st.info(
            "EDA image files were not found in assets/eda/. "
            "The interactive dataset charts above are still available."
        )

    st.divider()

    st.subheader("Dataset Preview")

    if dataset is not None:

        st.write(f"Loaded dataset: **{len(dataset):,} records**")

        st.dataframe(
            dataset.head(10),
            use_container_width=True
        )

    else:

        st.warning(
            "Processed dataset CSV was not found. "
            "Place the cleaned CSV inside the data folder "
            "to enable the dataset preview."
        )

    st.caption(
        "Dataset statistics are based on the cleaned dataset "
        "used in the model training experiment."
    )


# =========================================================
# PAGE 3: MODEL PERFORMANCE
# =========================================================

elif page == "Model Performance":

    st.header("Machine Learning Model Performance")

    st.write(
        "Comparison of the three machine learning classifiers "
        "evaluated using the held-out test dataset."
    )

    metrics_df = pd.DataFrame(MODEL_METRICS).T.reset_index()

    metrics_df.rename(
        columns={"index": "Model"},
        inplace=True
    )

    st.subheader("Model Comparison")

    st.dataframe(
        metrics_df.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    selected_metric = st.selectbox(
        "Select Evaluation Metric",
        ["Accuracy", "Precision", "Recall", "F1 Score"]
    )

    chart_df = pd.DataFrame({
        "Model": list(MODEL_METRICS.keys()),
        selected_metric: [
            values[selected_metric]
            for values in MODEL_METRICS.values()
        ]
    })

    fig = px.bar(
        chart_df,
        x="Model",
        y=selected_metric,
        color="Model",
        text=selected_metric,
        range_y=[85, 100]
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1120",
        plot_bgcolor="#0b1120"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Evaluation Metrics")

    cols = st.columns(4)

    svm_metrics = MODEL_METRICS["Linear SVM"]

    for col, (name, value) in zip(
        cols,
        svm_metrics.items()
    ):

        col.metric(name, f"{value:.2f}%")

    st.divider()

    st.subheader("Linear SVM Confusion Matrix")

    # Rows: actual classes; columns: predicted classes
    # Order: Safe Email, Phishing Email
    confusion_matrix = [
        [2162, 34],
        [32, 1277]
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=confusion_matrix,
            x=["Predicted Safe", "Predicted Phishing"],
            y=["Actual Safe", "Actual Phishing"],
            text=confusion_matrix,
            texttemplate="%{text}",
            colorscale="Blues"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1120",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "The confusion matrix represents the held-out test set "
        "for the Linear SVM model."
    )

    st.info(
        "The deployed message classifier uses Linear SVM. "
        "Its test accuracy was 98.12% on the phishing email dataset. "
        "This is not a guarantee of real-world financial scam detection accuracy."
    )


# =========================================================
# PAGE 4: SCAM ANALYSIS
# =========================================================

elif page == "Scam Analysis":

    st.header("Financial Scam Detection")

    st.write(
        "Submit a suspicious email, SMS or payment-related "
        "communication for multi-agent analysis."
    )

    message = st.text_area(
        "Enter a suspicious message",
        placeholder="Paste your email, SMS or payment message here...",
        height=200,
        key="scam_message"
    )

    analyze_col, clear_col = st.columns([1, 5])

    with analyze_col:

        analyze_clicked = st.button(
            "🔍 Analyse Message",
            type="primary",
            use_container_width=True
        )

    with clear_col:

        clear_clicked = st.button(
            "Clear Results",
            use_container_width=True
        )

    if clear_clicked:

        st.session_state.analysis_result = None
        st.session_state.analysis_message = ""
        st.rerun()

    if analyze_clicked:

        if message.strip():

            try:

                with st.spinner(
                    "Running all five ScamShield AI agents..."
                ):

                    result = run_scamshield(message)

                st.session_state.analysis_result = result
                st.session_state.analysis_message = message

                save_analysis(message, result)

                st.success("Analysis completed successfully.")

            except Exception as error:

                st.error("An error occurred during analysis.")
                st.exception(error)

        else:

            st.warning("Please enter a message before analysing.")

    result = st.session_state.analysis_result

    if result:

        st.divider()

        st.subheader("Analysis Results")

        message_result = result.get("message_result", {})
        url_results = result.get("url_results", [])
        impersonation = result.get("impersonation_result", {})
        payment = result.get("payment_result", {})
        explanation = result.get("explanation_result", {})

        overall_risk = result.get(
            "overall_risk",
            explanation.get("overall_risk", "Unknown")
        )

        # Overall risk
        if overall_risk == "High":

            st.error("🚨 HIGH RISK - Potential Scam Detected")

        elif overall_risk == "Medium":

            st.warning("⚠️ MEDIUM RISK - Suspicious Indicators Found")

        elif overall_risk == "Low":

            st.success("LOW RISK - Fewer Suspicious Indicators Detected")

        else:

            st.info(f"Risk Level: {overall_risk}")

        st.divider()

        # Agent 1
        with st.expander("1. Message Analysis Agent", expanded=True):

            st.write(
                "**Prediction:**",
                message_result.get("prediction", "Unknown")
            )

            st.write(
                "**Analysis:**",
                message_result.get("message", "No explanation available.")
            )

        # Agent 2
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

                    for indicator in item.get("indicators", []):

                        st.write(f"- {indicator}")

                    if not item.get("indicators"):

                        st.write("No heuristic indicators detected.")

                    st.caption(item.get("reputation_message", ""))

                    st.divider()

            else:

                st.info("No URLs detected in the submitted message.")

        # Agent 3
        with st.expander("3. Impersonation Detection Agent", expanded=True):

            st.metric(
                "Risk Score",
                impersonation.get("risk_score", 0)
            )

            st.write("**Risk Level:**", impersonation.get("risk_level", "Unknown"))

            for label, key in [
                ("Brand Mentions", "brand_mentions"),
                ("Authority Mentions", "authority_mentions"),
                ("Urgency Indicators", "urgency_indicators"),
                ("Sensitive Requests", "sensitive_requests")
            ]:

                values = impersonation.get(key, [])

                st.write(
                    f"**{label}:**",
                    ", ".join(values) if values else "None"
                )

            st.write(
                "**Explanation:**",
                impersonation.get("explanation", "No explanation available.")
            )

        # Agent 4
        with st.expander("4. Payment Risk Assessment Agent", expanded=True):

            st.metric(
                "Risk Score",
                payment.get("risk_score", 0)
            )

            st.write("**Risk Level:**", payment.get("risk_level", "Unknown"))

            for label, key in [
                ("Payment Indicators", "payment_indicators"),
                ("Urgency Indicators", "urgency_indicators"),
                ("Sensitive Requests", "sensitive_requests"),
                ("Alternative Payment Methods", "alternative_payment_methods"),
                ("Payment Link Indicators", "payment_link_indicators")
            ]:

                values = payment.get(key, [])

                st.write(
                    f"**{label}:**",
                    ", ".join(values) if values else "None"
                )

            st.write(
                "**Explanation:**",
                payment.get("explanation", "No explanation available.")
            )

        # Agent 5
        with st.expander("5. AI Explanation Agent", expanded=True):

            st.write(
                "**Gemini Status:**",
                explanation.get("llm_status", "Unknown")
            )

            st.markdown(
                explanation.get(
                    "ai_explanation",
                    "AI explanation is not available."
                )
            )

        # Recommendations shown once
        st.subheader("Security Recommendations")

        recommendations = explanation.get("recommendations", [])

        if recommendations:

            for recommendation in recommendations:

                st.markdown(f"- {recommendation}")

        else:

            st.info("No recommendations available.")

        with st.expander("Detailed Evidence Summary"):

            evidence = explanation.get("evidence", [])

            if evidence:

                for item in evidence:

                    st.write(f"- {item}")

            else:

                st.write("No additional evidence available.")

        st.divider()

        st.caption(
            "ScamShield AI provides automated risk screening. "
            "A Low risk result does not guarantee that a message is safe."
        )


# =========================================================
# PAGE 5: ANALYSIS HISTORY
# =========================================================

elif page == "Analysis History":

    st.header("Analysis History")

    history = get_history()

    if history.empty:

        st.info(
            "No analysis records yet. Visit Scam Analysis "
            "and analyse a message to create your first record."
        )

    else:

        c1, c2, c3 = st.columns(3)

        c1.metric("Total Analyses", len(history))

        c2.metric(
            "High Risk",
            len(history[history["overall_risk"] == "High"])
        )

        c3.metric(
            "Phishing Predictions",
            len(history[history["prediction"] == "Phishing Email"])
        )

        st.divider()

        st.subheader("Risk Distribution")

        risk_df = (
            history["overall_risk"]
            .value_counts()
            .rename_axis("Risk Level")
            .reset_index(name="Count")
        )

        fig = px.pie(
            risk_df,
            names="Risk Level",
            values="Count",
            hole=0.5,
            color="Risk Level",
            color_discrete_map={
                "High": "#ef4444",
                "Medium": "#f59e0b",
                "Low": "#22c55e"
            }
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1120"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        st.subheader("Recent Analyses")

        display_history = history.drop(columns=["id"])

        st.dataframe(
            display_history,
            use_container_width=True,
            hide_index=True
        )

        csv_data = history.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Analysis History",
            data=csv_data,
            file_name="scamshield_analysis_history.csv",
            mime="text/csv"
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "ScamShield AI | Agentic Financial Scam Detection & Risk Assessment"
)
