"""
base_engine.py — Abstract base class for all fraud risk engines.

Every risk engine in the plugin-based fraud evaluation pipeline must
subclass :class:`RiskEngine` and implement the :meth:`evaluate` method.
This contract ensures that the :class:`~app.services.risk_orchestrator.RiskOrchestrator`
can call any engine interchangeably, making the system open for extension
without requiring modifications to the core pipeline.

Usage example::

    from app.risk_engines.base_engine import RiskEngine

    class MyCustomEngine(RiskEngine):
        name = "my_custom_engine"

        def evaluate(self, db, context: dict) -> dict:
            # … custom fraud signal logic …
            return {"score": 0.0, "details": {}}
"""

from abc import ABC, abstractmethod


class RiskEngine(ABC):
    """
    Abstract base class for pluggable fraud risk engines.

    Attributes
    ----------
    name : str
        A unique, human-readable identifier for the engine (e.g.
        ``"rule_engine"``).  Subclasses **must** define this as a class-level
        attribute.  The orchestrator uses it as the key in its result
        dictionaries, so the value must be stable across deployments.

    Methods
    -------
    evaluate(db, context) -> dict
        Run the engine's fraud signal logic and return a structured result.
        See :meth:`evaluate` for the required return schema.
    """

    #: Unique identifier for the engine.  Override in each subclass.
    name: str

    @abstractmethod
    def evaluate(self, db, context: dict) -> dict:
        """
        Evaluate fraud risk for the given transaction context.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Active database session used for any persistence queries required
            by the engine's underlying service.
        context : dict
            Shared evaluation context produced by the orchestrator.  At
            minimum the orchestrator guarantees the following keys:

            * ``"transaction"`` (dict) — raw transaction payload.
            * ``"merchant_id"`` (str | None) — merchant identifier.
            * ``"device_hash"`` (str | None) — device fingerprint hash.
            * ``"scores"`` (dict) — scores collected from engines that have
              already run in the current pipeline execution.  Engines that
              run later in the sequence can use this to incorporate upstream
              signals (e.g. the ML engine reads the rule score).

        Returns
        -------
        dict
            A structured result with **at least** the following keys:

            * ``"score"`` (float) — normalised fraud risk score in the range
              ``[0, 1]`` (or an unnormalised integer score for rule-based
              engines).
            * ``"details"`` (dict) — engine-specific diagnostic payload that
              callers and downstream systems can inspect for explainability.

        Raises
        ------
        NotImplementedError
            If a subclass does not implement this method.
        """
