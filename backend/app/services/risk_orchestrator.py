from app.services.fraud_signals import calculate_risk_score
from app.services.device_risk import detect_device_risk
from app.services.fraud_ml_prediction import predict_chargeback
from app.services.reputation_service import get_reputation
from app.services.fraud_graph_analysis import analyze_entity_cluster
from app.services.global_intelligence import check_global_device_risk


class RiskOrchestrator:
    """
    Central fraud decision engine.

    Combines multiple fraud intelligence systems into
    a single unified risk evaluation.
    """

    def __init__(self, db):
        self.db = db

    def evaluate_transaction(self, transaction, device_hash, email=None):
        """
        Run the full fraud intelligence stack.
        """

        results = {}

        # Rule Engine
        rule_score = calculate_risk_score(
            self.db,
            transaction,
            transaction.get("id")
        )

        results["rule_score"] = rule_score

        # Device Intelligence
        device_result = detect_device_risk(self.db, device_hash)

        results["device_risk"] = device_result

        # Global Device Intelligence
        global_device = check_global_device_risk(self.db, device_hash)

        results["global_device_risk"] = global_device

        # Reputation System
        if email:
            reputation = get_reputation(self.db, "email", email)
        else:
            reputation = {"reputation_score": 0}

        results["reputation"] = reputation

        # Graph Fraud Detection
        cluster_result = analyze_entity_cluster(
            self.db,
            f"device_{device_hash}"
        )

        results["fraud_graph"] = cluster_result

        # ML Prediction
        ml_prediction = predict_chargeback(
            transaction.get("amount"),
            rule_score
        )

        results["ml_prediction"] = ml_prediction

        # Final Risk Score Calculation
        final_score = self._combine_scores(results)

        results["final_risk_score"] = final_score

        return results

    def _combine_scores(self, signals):
        """
        Weighted risk scoring engine.
        """

        rule = signals["rule_score"]
        device = signals["device_risk"]["usage_count"]
        reputation = signals["reputation"]["reputation_score"]
        graph = signals["fraud_graph"]["cluster_risk_score"]
        ml = signals["ml_prediction"]["chargeback_probability"]

        score = (
            (rule * 0.25)
            + (min(device / 10, 1) * 0.15)
            + (graph * 0.20)
            + (ml * 0.30)
            + (reputation * 0.10)
        )

        return round(min(score, 1), 3)