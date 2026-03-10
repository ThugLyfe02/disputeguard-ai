"""
ml_engine.py — Machine learning chargeback prediction engine.

Wraps :func:`app.services.fraud_ml_prediction.predict_chargeback` to provide
an ML-based fraud risk signal within the plugin-based pipeline.

Because the ML model combines multiple upstream fraud signals, this engine
consumes scores that have already been collected by earlier engines in the
same orchestrator run.  The orchestrator stores accumulated scores under the
``"scores"`` key in the shared evaluation context, keyed by engine name.
This engine reads from that key so that rule and device scores inform the
prediction without tight coupling between engines.

Example::

    from app.risk_engines.ml_engine import MLEngine

    engine = MLEngine()
    result = engine.evaluate(db, context)
    # result == {
    #     "score": 0.8731,
    #     "details": {
    #         "chargeback_probability": 0.8731,
    #         "risk_level": "high",
    #         "features_used": {...}
    #     }
    # }
"""

from app.risk_engines.base_engine import RiskEngine
from app.services.fraud_ml_prediction import predict_chargeback


class MLEngine(RiskEngine):
    """
    Fraud risk engine based on machine-learning chargeback prediction.

    Delegates to :func:`~app.services.fraud_ml_prediction.predict_chargeback`,
    passing the transaction amount and any upstream engine scores that are
    already present in the shared ``context["scores"]`` dict.

    Attributes
    ----------
    name : str
        Engine identifier — ``"ml_engine"``.
    """

    name = "ml_engine"

    def evaluate(self, db, context: dict) -> dict:
        """
        Predict chargeback probability using ML.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Active database session (not used directly by this engine but
            accepted for interface consistency).
        context : dict
            Orchestrator evaluation context.  Reads the following keys:

            * ``"transaction"`` (dict) — must contain ``"amount"`` (float).
            * ``"scores"`` (dict) — accumulated engine scores from engines
              that ran before this one in the current orchestrator execution.
              Expected sub-keys (all optional, default to ``0``):

              - ``"rule_engine"`` — output of :class:`~app.risk_engines.rule_engine.RuleEngine`.
              - ``"device_engine"`` — output of :class:`~app.risk_engines.device_engine.DeviceEngine`.
              - ``"graph_engine"`` — output of :class:`~app.risk_engines.graph_engine.GraphEngine`.

        Returns
        -------
        dict
            * ``"score"`` (float) — chargeback probability in ``[0, 1]``.
            * ``"details"`` (dict) — full payload from
              :func:`~app.services.fraud_ml_prediction.predict_chargeback`,
              including ``risk_level`` and the feature vector used.
        """
        transaction = context.get("transaction", {})
        amount = float(transaction.get("amount", 0))

        # Read scores contributed by upstream engines in this pipeline run.
        scores = context.get("scores", {})
        rule_score = float(scores.get("rule_engine", 0))
        device_risk_score = float(scores.get("device_engine", 0))
        # "reputation_engine" is not yet a registered plugin engine; until a
        # ReputationEngine is added to the orchestrator this defaults to 0.
        reputation_score = float(scores.get("reputation_engine", 0))
        cluster_risk_score = float(scores.get("graph_engine", 0))

        result = predict_chargeback(
            amount=amount,
            rule_score=rule_score,
            device_risk_score=device_risk_score,
            reputation_score=reputation_score,
            cluster_risk_score=cluster_risk_score,
        )

        probability = float(result.get("chargeback_probability", 0.0))
        confidence = float(result.get("prediction_confidence", 0.0))

        # When the model has very little training data, reduce its influence.
        score = probability * confidence if confidence < 0.3 else probability

        return {
            "score": score,
            "details": result,
        }
