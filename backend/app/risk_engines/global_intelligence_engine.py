"""
Global Fraud Intelligence Engine

Evaluates entity risk across the entire platform.

Detects signals like:

• devices reused across merchants
• emails associated with chargebacks
• IP fraud clusters
• suspicious global transaction patterns

This engine allows DisputeGuard AI to behave like a
network-level fraud intelligence platform.
"""

from app.risk_engines.base_engine import RiskEngine
from sqlalchemy.orm import Session


class GlobalIntelligenceEngine(RiskEngine):

    name = "global_intelligence_engine"

    def evaluate(self, db: Session, context: dict):

        device_hash = context.get("device_hash")
        transaction = context.get("transaction", {})

        email = transaction.get("email")
        ip = transaction.get("ip")

        risk_score = 0
        details = {}

        # --------------------------------------------------
        # Device reuse across merchants
        # --------------------------------------------------

        if device_hash:

            merchants = db.execute(
                """
                SELECT COUNT(DISTINCT merchant_id)
                FROM device_fingerprint
                WHERE device_hash = :device
                """,
                {"device": device_hash},
            ).scalar()

            merchants = merchants or 0

            if merchants >= 3:
                risk_score += 0.4

            details["device_cross_merchant_count"] = merchants

        # --------------------------------------------------
        # Email fraud history
        # --------------------------------------------------

        if email:

            disputes = db.execute(
                """
                SELECT COUNT(*)
                FROM disputes
                WHERE email = :email
                """,
                {"email": email},
            ).scalar()

            disputes = disputes or 0

            if disputes >= 2:
                risk_score += 0.3

            details["email_dispute_count"] = disputes

        # --------------------------------------------------
        # IP fraud signals
        # --------------------------------------------------

        if ip:

            suspicious = db.execute(
                """
                SELECT COUNT(*)
                FROM transactions
                WHERE ip_address = :ip
                AND risk_score > 0.8
                """,
                {"ip": ip},
            ).scalar()

            suspicious = suspicious or 0

            if suspicious >= 5:
                risk_score += 0.3

            details["ip_high_risk_tx_count"] = suspicious

        return {
            "score": min(risk_score, 1.0),
            "details": details
        }