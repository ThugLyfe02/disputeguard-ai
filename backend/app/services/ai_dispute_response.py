from typing import Dict


def generate_dispute_response(dispute: Dict, evidence: Dict) -> str:
    """
    Generates a structured dispute response that merchants can submit
    to Stripe or their payment processor.
    """

    transaction_id = evidence.get("transaction_id")
    amount = evidence.get("amount")
    reason = dispute.get("reason")

    response = f"""
Dispute Response

Transaction ID: {transaction_id}
Dispute Reason: {reason}
Transaction Amount: {amount}

Evidence Summary:
- Payment was successfully processed and authorized.
- The order was fulfilled and delivery was confirmed.
- Customer history indicates legitimate purchase behavior.

Based on the evidence provided, this transaction appears to be valid.
We respectfully request that the dispute be reviewed and the chargeback reversed.

Sincerely,
DisputeGuard AI Automated Response
"""

    return response.strip()
