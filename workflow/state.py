
from typing import TypedDict, List, Dict, Any


class ScamShieldState(TypedDict, total=False):

    # Original user input
    message: str

    # Message Analysis Agent
    message_result: Dict[str, Any]

    # URL Intelligence Agent
    url_results: List[Dict[str, Any]]

    # Impersonation Detection Agent
    impersonation_result: Dict[str, Any]

    # Payment Risk Agent
    payment_result: Dict[str, Any]

    # Explanation Agent
    explanation_result: Dict[str, Any]

    # Final assessment
    overall_risk: str

    # Error tracking
    errors: List[str]
