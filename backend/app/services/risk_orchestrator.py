"""
risk_orchestrator.py — Plugin-based fraud risk orchestration engine.

The :class:`RiskOrchestrator` accepts an ordered list of
:class:`~app.risk_engines.base_engine.RiskEngine` instances and runs them
sequentially against a shared evaluation context.  After each engine
completes, its score is added to ``context["scores"]`` so that later engines
(e.g. :class:`~app.risk_engines.ml_engine.MLEngine`) can incorporate upstream
signals without tight coupling.

This design mirrors Stripe Radar's layered rule / ML pipeline and Shopify's
modular fraud-signal architecture:  new engines can be plugged in without
modifying any existing code.

Typical usage::

    from app.risk_engines import (
        RuleEngine, DeviceEngine, MLEngine,
        GraphEngine, CrossMerchantEngine,
    )
    from app.services.risk_orchestrator import RiskOrchestrator

    context = {
        "transaction": transaction,
        "merchant_id": merchant_id,
        "device_hash": device_hash,
    }

    orchestrator = RiskOrchestrator(engines=[
        RuleEngine(),
        DeviceEngine(),
        GraphEngine(),
        CrossMerchantEngine(),
        MLEngine(),
    ])

    result = orchestrator.evaluate(db, context)
    # result == {
    #     "engines": {
    #         "rule_engine": {"score": 55.0, "details": {...}},
    #         ...
    #     },
    #     "scores": {"rule_engine": 55.0, ...},
    #     "final_risk_score": 0.4321,
    # }
"""

import logging
from typing import List

from app.risk_engines.base_engine import RiskEngine

logger = logging.getLogger("disputeguard.orchestrator")


class RiskOrchestrator:
    """
    Plugin-based fraud risk orchestrator.

    Accepts an ordered list of :class:`~app.risk_engines.base_engine.RiskEngine`
    instances, runs them sequentially, and aggregates their outputs into a
    single structured result.

    The orchestrator is intentionally stateless with respect to the database
    and the transaction context — both are supplied at evaluation time so the
    same orchestrator instance can be reused across requests.

    Parameters
    ----------
    engines : list[RiskEngine]
        Ordered sequence of fraud risk engines to execute.  Engines that
        appear earlier in the list produce scores that are visible to later
        engines via ``context["scores"]``, enabling sequential signal
        enrichment without tight coupling.

    Attributes
    ----------
    engines : list[RiskEngine]
        The engine instances registered with this orchestrator.

    Examples
    --------
    ::

        orchestrator = RiskOrchestrator(engines=[RuleEngine(), MLEngine()])
        result = orchestrator.evaluate(db, context)
    """

    def __init__(self, engines: List[RiskEngine]):
        self.engines = engines

    def evaluate(self, db, context: dict) -> dict:
        """
        Run all registered engines and return a structured risk assessment.

        Each engine receives a copy of *context* enriched with the ``"scores"``
        dict accumulated so far.  The dict is updated in-place after every
        engine completes, so later engines have access to earlier scores.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Active database session forwarded to every engine.
        context : dict
            Base evaluation context.  Must include at minimum:

            * ``"transaction"`` (dict) — raw transaction payload.
            * ``"merchant_id"`` (str | None) — merchant identifier.
            * ``"device_hash"`` (str | None) — device fingerprint hash.

        Returns
        -------
        dict
            Structured orchestration result with three top-level keys:

            * ``"engines"`` (dict[str, dict]) — per-engine result dicts
              keyed by :attr:`~app.risk_engines.base_engine.RiskEngine.name`.
              Each value contains ``"score"`` and ``"details"``.
            * ``"scores"`` (dict[str, float]) — flat mapping of engine name
              to its numeric score.  Convenient for downstream aggregation.
            * ``"final_risk_score"`` (float) — arithmetic mean of all engine
              scores, rounded to 4 decimal places.  Callers that require
              weighted aggregation should compute their own composite from
              the ``"scores"`` dict.
        """
        engines_output: dict = {}

        # scores is mutated in-place so each engine sees upstream results.
        scores: dict = {}

        running_context = dict(context)
        running_context["scores"] = scores

        for engine in self.engines:
            try:
                result = engine.evaluate(db, running_context)
                engines_output[engine.name] = result
                scores[engine.name] = result.get("score", 0.0)
            except Exception:
                logger.exception(
                    "Engine '%s' failed — using fallback score 0.5",
                    engine.name,
                )
                engines_output[engine.name] = {
                    "score": 0.5,
                    "details": {"error": "engine_failed"},
                }
                scores[engine.name] = 0.5

        # Guard against an empty engine list: return 0.0 rather than raising
        # ZeroDivisionError.  Callers should always supply at least one engine.
        final_risk_score = (
            round(sum(scores.values()) / len(scores), 4)
            if scores
            else 0.0
        )

        return {
            "engines": engines_output,
            "scores": scores,
            "final_risk_score": final_risk_score,
        }