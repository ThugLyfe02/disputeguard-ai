"""
cross_merchant_engine.py — Cross-merchant fraud activity detection engine.

Wraps :func:`app.services.cross_merchant_intelligence.detect_cross_merchant_activity`
to surface cross-merchant device activity as a fraud signal within the
plugin-based pipeline.

A device hash that has been used across more than one merchant is flagged as
suspicious.  This engine converts the binary ``suspicious`` flag from the
underlying service into a numeric score (``1.0`` for suspicious, ``0.0``
otherwise) so it integrates naturally with the orchestrator's scoring model.

Example::

    from app.risk_engines.cross_merchant_engine import CrossMerchantEngine

    engine = CrossMerchantEngine()
    result = engine.evaluate(db, context)
    # result == {
    #     "score": 1.0,
    #     "details": {
    #         "device_hash": "abc123",
    #         "merchant_count": 3,
    #         "merchants": ["m1", "m2", "m3"],
    #         "suspicious": True
    #     }
    # }
"""

from app.risk_engines.base_engine import RiskEngine
from app.services.cross_merchant_intelligence import detect_cross_merchant_activity


class CrossMerchantEngine(RiskEngine):
    """
    Fraud risk engine based on cross-merchant device activity.

    Delegates to
    :func:`~app.services.cross_merchant_intelligence.detect_cross_merchant_activity`
    to detect whether a device has been observed across multiple merchants, a
    pattern strongly correlated with coordinated fraud campaigns.

    Attributes
    ----------
    name : str
        Engine identifier — ``"cross_merchant_engine"``.
    """

    name = "cross_merchant_engine"

    def evaluate(self, db, context: dict) -> dict:
        """
        Detect cross-merchant fraud activity for the device in *context*.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Active database session forwarded to the underlying service.
        context : dict
            Orchestrator evaluation context.  Must contain:

            * ``"device_hash"`` (str | None) — device fingerprint hash to
              evaluate for cross-merchant activity.

        Returns
        -------
        dict
            * ``"score"`` (float) — ``1.0`` if the device is flagged as
              suspicious (seen at more than one merchant), ``0.0`` otherwise.
            * ``"details"`` (dict) — full payload returned by
              :func:`~app.services.cross_merchant_intelligence.detect_cross_merchant_activity`,
              including ``merchant_count`` and the list of ``merchants``.
        """
        device_hash = context.get("device_hash")

        result = detect_cross_merchant_activity(db, device_hash)

        score = 1.0 if result.get("suspicious", False) else 0.0

        return {
            "score": score,
            "details": result,
        }
