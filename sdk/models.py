from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Transaction:
    """
    Represents a transaction to be evaluated by the fraud platform.
    """

    id: str
    customer_id: str
    amount: float


@dataclass
class FraudEvaluationResult:
    """
    Represents the structured response returned by the fraud platform.
    """

    transaction_id: str
    fraud_signals: Dict[str, Any]
    device_reputation: Dict[str, Any]
    graph_risk: Dict[str, Any]
    threat_intelligence: Dict[str, Any]
    investigation_report: Dict[str, Any]
    defense_actions: Dict[str, Any]
