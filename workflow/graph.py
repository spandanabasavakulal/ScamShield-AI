
from langgraph.graph import StateGraph, START, END

from workflow.state import ScamShieldState

from models.predict import predict_email
from agents.url_intelligence import analyze_message_urls
from agents.impersonation_detection import analyze_impersonation
from agents.payment_risk import analyze_payment_risk
from agents.explanation import generate_explanation


# ==========================================
# 1. MESSAGE ANALYSIS NODE
# ==========================================

def message_analysis_node(state: ScamShieldState):

    result = predict_email(state["message"])

    return {
        "message_result": result
    }


# ==========================================
# 2. URL INTELLIGENCE NODE
# ==========================================

def url_intelligence_node(state: ScamShieldState):

    results = analyze_message_urls(state["message"])

    return {
        "url_results": results
    }


# ==========================================
# 3. IMPERSONATION DETECTION NODE
# ==========================================

def impersonation_detection_node(state: ScamShieldState):

    result = analyze_impersonation(state["message"])

    return {
        "impersonation_result": result
    }


# ==========================================
# 4. PAYMENT RISK NODE
# ==========================================

def payment_risk_node(state: ScamShieldState):

    result = analyze_payment_risk(state["message"])

    return {
        "payment_result": result
    }


# ==========================================
# 5. EXPLANATION NODE
# ==========================================

def explanation_node(state: ScamShieldState):

    result = generate_explanation(
        message_result=state.get("message_result"),
        url_results=state.get("url_results"),
        impersonation_result=state.get("impersonation_result"),
        payment_result=state.get("payment_result")
    )

    return {
        "explanation_result": result,
        "overall_risk": result["overall_risk"]
    }


# ==========================================
# 6. BUILD LANGGRAPH WORKFLOW
# ==========================================

workflow = StateGraph(ScamShieldState)

# Register agents as nodes
workflow.add_node("message_analysis", message_analysis_node)
workflow.add_node("url_intelligence", url_intelligence_node)
workflow.add_node("impersonation_detection", impersonation_detection_node)
workflow.add_node("payment_risk", payment_risk_node)
workflow.add_node("explanation", explanation_node)

# Define execution sequence
workflow.add_edge(START, "message_analysis")
workflow.add_edge("message_analysis", "url_intelligence")
workflow.add_edge("url_intelligence", "impersonation_detection")
workflow.add_edge("impersonation_detection", "payment_risk")
workflow.add_edge("payment_risk", "explanation")
workflow.add_edge("explanation", END)

# Compile workflow
scamshield_graph = workflow.compile()


# ==========================================
# 7. RUN COMPLETE ANALYSIS
# ==========================================

def run_scamshield(message: str):

    if not isinstance(message, str) or not message.strip():
        raise ValueError("Please provide a valid message.")

    initial_state = {
        "message": message,
        "errors": []
    }

    result = scamshield_graph.invoke(initial_state)

    return result


# ==========================================
# 8. TESTING
# ==========================================

if __name__ == "__main__":

    sample_message = """
    Your SBI bank account will be blocked today!

    Verify your account immediately.
    Share your OTP to prevent suspension.

    Visit https://secure-bank.example/login
    """

    print("\nSCAMSHIELD AI - AGENTIC WORKFLOW")
    print("=" * 55)

    result = run_scamshield(sample_message)

    print("\nMESSAGE ANALYSIS:")
    print(result["message_result"])

    print("\nURL INTELLIGENCE:")
    print(result["url_results"])

    print("\nIMPERSONATION DETECTION:")
    print(result["impersonation_result"])

    print("\nPAYMENT RISK:")
    print(result["payment_result"])

    print("\nFINAL EXPLANATION:")
    print(result["explanation_result"])

    print("\nOVERALL RISK:", result["overall_risk"])

    print("=" * 55)
