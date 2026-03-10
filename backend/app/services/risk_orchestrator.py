"""
risk_orchestrator.py — Plugin-based fraud risk orchestration engine.

The :class:`RiskOrchestrator` accepts an ordered list of
:class:`~app.risk_engines.base_engine.RiskEngine` instances and runs them
sequentially against a shared evaluation context.  After each engine
completes, its score is added to ``context["scores"]`` so that later engines
(e.g. :class:`~app.risk_engines.ml_engine.MLEngine`) can incorporate upstream
signals without tight coupling.

Supports configurable weighted score aggregation — each engine's contribution
to the final risk score can be tuned via a weight map passed at construction.

This design mirrors Stripe Radar's layered rule / ML pipeline and Shopify's
modular fraud-signal architecture:  new engines can be plugged in without
modifying any existing code.

Typical usage::

    from app.services.risk_orchestrator import RiskOrchestrator

    orchestrator = RiskOrchestrator(engines=[RuleEngine(), MLEngine()])
    result = orchestrator.evaluate(db, context)
    # result == {
    #     "engines": {
    #         "rule_engine": {"score": 0.55, "details": {...}, "execution_time_ms": 1.2},
    #         ...
    #     },
    #     "scores": {"rule_engine": 0.55, ...},
    #     "final_risk_score": 0.4321,
    #     "pipeline_timing": {"total_ms": 12.5, "engines": {...}},
    # }
"""

import logging
import time
from typing import Dict, List, Optional

from app.risk_engines.base_engine import RiskEngine

logger = logging.getLogger("disputeguard.orchestrator")

# ---------------------------------------------------------------
# Default engine weights — tunable per deployment.
# Weights do not need to sum to 1.0; they are normalised internally.
# ---------------------------------------------------------------
DEFAULT_WEIGHTS: Dict[str, float] = {
    "rule_engine": 0.15,
    "device_engine": 0.15,
    "graph_engine": 0.12,
    "cross_merchant_engine": 0.10,
    "network_engine": 0.10,
    "fraud_network_engine": 0.13,
    "graph_feature_engine": 0.10,
    "ml_engine": 0.15,
}


class RiskOrchestrator:
    """
    Plugin-based fraud risk orchestrator with weighted aggregation.

    Parameters
    ----------
    engines : list[RiskEngine]
        Ordered sequence of fraud risk engines to execute.
    weights : dict[str, float] | None
        Optional mapping of engine name → weight.  Engines not present
        in the map receive equal share of the remaining weight.
        If *None*, :data:`DEFAULT_WEIGHTS` is used.
    """

    def __init__(
        self,
        engines: List[RiskEngine],
        weights: Optional[Dict[str, float]] = None,
    ):
        self.engines = engines
        self.weights = weights or DEFAULT_WEIGHTS

    def evaluate(self, db, context: dict) -> dict:
        """
        Run all registered engines and return a structured risk assessment.

        Each engine receives a copy of *context* enriched with the ``"scores"``
        dict accumulated so far.  The dict is updated in-place after every
        engine completes, so later engines have access to earlier scores.

        Returns
        -------
        dict
            * ``"engines"`` — per-engine results with ``execution_time_ms``.
            * ``"scores"`` — flat mapping of engine name to score.
            * ``"final_risk_score"`` — weighted aggregate score in [0, 1].
            * ``"pipeline_timing"`` — per-engine and total execution timing.
        """
        engines_output: dict = {}
        scores: dict = {}
        timings: dict = {}

        running_context = dict(context)
        running_context["scores"] = scores

        pipeline_start = time.monotonic()

        for engine in self.engines:
            engine_start = time.monotonic()
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

            elapsed_ms = round((time.monotonic() - engine_start) * 1000, 2)
            engines_output[engine.name]["execution_time_ms"] = elapsed_ms
            timings[engine.name] = elapsed_ms

        total_ms = round((time.monotonic() - pipeline_start) * 1000, 2)

        # ----------------------------------------------------------
        # Weighted score aggregation
        # ----------------------------------------------------------
        final_risk_score = self._weighted_score(scores)

        return {
            "engines": engines_output,
            "scores": scores,
            "final_risk_score": final_risk_score,
            "pipeline_timing": {
                "total_ms": total_ms,
                "engines": timings,
            },
        }

    def _weighted_score(self, scores: dict) -> float:
        """
        Compute weighted aggregate of engine scores.

        Engines present in ``self.weights`` use their configured weight.
        Engines absent from the weight map receive a fallback weight
        equal to ``1 / len(scores)`` so new engines contribute without
        requiring a weight map update.
        """
        if not scores:
            return 0.0

        fallback_weight = 1.0 / len(scores)
        total_weight = 0.0
        weighted_sum = 0.0

        for name, score in scores.items():
            w = self.weights.get(name, fallback_weight)
            weighted_sum += score * w
            total_weight += w

        if total_weight == 0:
            return 0.0

        return round(weighted_sum / total_weight, 4)
