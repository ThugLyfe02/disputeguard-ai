import logging

from app.services.fraud_pipeline import run_fraud_pipeline
from app.services.reputation_service import get_reputation
from app.services.fraud_graph_analysis import analyze_entity_cluster

logger = logging.getLogger(__name__)


"""
Fraud Decision Engine

Central orchestrator that combines:

• Rule-based fraud detection
• Device fingerprint risk
• Graph fraud detection
• Reputation scoring
• Machine learning predictions

Produces a unified fraud risk decision.
"""


class FraudDecisionEngine:

    def __init__(self, db):
        self.db = db

    def evaluate_transaction(self, transaction, device_hash, merchant_id):
        """
        Perform full fraud intelligence analysis.
        """

        logger.info("Running fraud pipeline")

        pipeline_result = run_fraud_pipeline(
            self.db,
            transaction,
            device_hash
        )

        logger.info("Running reputation analysis")

        reputation = get_reputation(
            self.db,
            "customer",
            transaction.get("customer_id")
        )

        logger.info("Running graph fraud analysis")

        graph_result = analyze_entity_cluster(
            self.db,
            f"tx_{transaction.get('id')}"
        )

        final_score = self._combine_scores(
            pipeline_result,
            reputation,
            graph_result
        )

        return {
            "pipeline": pipeline_result,
            "reputation": reputation,
            "graph_analysis": graph_result,
            "final_risk_score": final_score,
            "decision": self._make_decision(final_score)
        }

    def _combine_scores(self, pipeline, reputation, graph):
        """
        Combine multiple intelligence sources into a unified score.
        """

        rule_score = pipeline["rule_score"]
        device_risk = pipeline["device_risk"]["usage_count"]
        ml_prob = pipeline["ml_prediction"]["chargeback_probability"]
        reputation_score = reputation.get("reputation_score", 0)
        cluster_score = graph["cluster_risk_score"]

        combined = (
            rule_score * 0.25 +
            device_risk * 0.15 +
            ml_prob * 0.35 +
            reputation_score * 0.10 +
            cluster_score * 0.15
        )

        return round(combined, 3)

    def _make_decision(self, score):

        if score > 0.8:
            return "block"

        if score > 0.6:
            return "review"

        return "approve"