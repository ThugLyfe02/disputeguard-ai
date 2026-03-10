"""
rule_engine.py — Rule-based fraud risk engine.

This engine delegates to :func:`app.services.fraud_signals.calculate_risk_score`
to evaluate classic rule-based fraud signals such as unusually high transaction
amounts and IP-to-billing-country mismatches.

The raw rule score is normalised to ``[0, 1]`` by dividing by 100 and
clamping.  For example, a high-amount signal (30) plus an IP mismatch (25)
yields a raw score of 55, which is returned as ``0.55``.

Example::

    from app.risk_engines.rule_engine import RuleEngine

    engine = RuleEngine()
    result = engine.evaluate(db, context)
    # result == {"score": 0.55, "details": {"transaction_id": "txn_123"}}
"""

from app.risk_engines.base_engine import RiskEngine
from app.services.fraud_signals import calculate_risk_score


class RuleEngine(RiskEngine):
    """
    Fraud risk engine based on hard-coded business rules.

    Calls :func:`~app.services.fraud_signals.calculate_risk_score` with the
    ``transaction`` and ``transaction_id`` extracted from the shared
    evaluation context.

    Attributes
    ----------
    name : str
        Engine identifier — ``"rule_engine"``.
    """

    name = "rule_engine"

    def evaluate(self, db, context: dict) -> dict:
        """
        Evaluate rule-based fraud signals for the transaction in *context*.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Active database session passed through to the underlying service.
        context : dict
            Orchestrator evaluation context.  Must contain a ``"transaction"``
            key whose value is the raw transaction dict (with at minimum an
            ``"id"`` key).

        Returns
        -------
        dict
            * ``"score"`` (float) — normalised rule score in ``[0, 1]`` (e.g. 0.55).
            * ``"details"`` (dict) — ``{"transaction_id": str}`` for
              traceability.
        """
        transaction = context.get("transaction", {})
        transaction_id = transaction.get("id")

        score = calculate_risk_score(db, transaction, transaction_id)

        return {
            "score": min(float(score) / 100.0, 1.0),
            "details": {
                "transaction_id": transaction_id,
            },
        }
