from app.services.fraud_explainer import explain_fraud_signals
from app.services.fraud_report_builder import build_fraud_report
from app.services.fraud_pipeline import run_fraud_pipeline


def investigate_transaction(db, transaction, device_hash):
    """
    Performs a full fraud investigation for a transaction.
    """

    signals = run_fraud_pipeline(db, transaction, device_hash)

    explanations = explain_fraud_signals(signals)

    report = build_fraud_report(
        entity=transaction.get("id"),
        signals=signals,
        explanations=explanations
    )

    return report