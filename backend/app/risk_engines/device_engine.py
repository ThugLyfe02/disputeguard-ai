"""
device_engine.py — Device fingerprint fraud risk engine.

Wraps :func:`app.services.device_risk.detect_device_risk` to evaluate the
fraud risk associated with a device fingerprint within the plugin-based
pipeline.

The engine extracts the ``device_hash`` and ``merchant_id`` from the shared
evaluation context, delegates scoring to the underlying service, and returns a
normalised score along with the full diagnostic payload from the service.

Example::

    from app.risk_engines.device_engine import DeviceEngine

    engine = DeviceEngine()
    result = engine.evaluate(db, context)
    # result == {
    #     "score": 0.42,
    #     "details": {
    #         "device_hash": "abc123",
    #         "risk_score": 0.42,
    #         "risk_level": "medium",
    #         ...
    #     }
    # }
"""

from app.risk_engines.base_engine import RiskEngine
from app.services.device_risk import detect_device_risk


class DeviceEngine(RiskEngine):
    """
    Fraud risk engine based on device fingerprint intelligence.

    Delegates to :func:`~app.services.device_risk.detect_device_risk` to
    analyse total device usage, merchant-specific usage, and historical
    dispute ratios associated with the device hash.

    Attributes
    ----------
    name : str
        Engine identifier — ``"device_engine"``.
    """

    name = "device_engine"

    def evaluate(self, db, context: dict) -> dict:
        """
        Evaluate device fingerprint fraud risk.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Active database session forwarded to the underlying service.
        context : dict
            Orchestrator evaluation context.  Must contain:

            * ``"device_hash"`` (str | None) — device fingerprint hash.
            * ``"merchant_id"`` (str | None) — merchant identifier used for
              tenant-safe scoring (optional but recommended).

        Returns
        -------
        dict
            * ``"score"`` (float) — normalised device risk score in ``[0, 1]``.
            * ``"details"`` (dict) — full payload returned by
              :func:`~app.services.device_risk.detect_device_risk`, including
              ``risk_level``, ``dispute_ratio``, etc.
        """
        device_hash = context.get("device_hash")
        merchant_id = context.get("merchant_id")

        result = detect_device_risk(db, device_hash, merchant_id)

        return {
            "score": float(result.get("risk_score", 0.0)),
            "details": result,
        }
