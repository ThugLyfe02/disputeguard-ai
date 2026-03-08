from app.services.fraud_graph import FraudGraph
from app.models.dispute import Dispute
from app.models.transaction import Transaction


def score_fraud_cluster(db, cluster):

    dispute_count = 0
    transaction_count = 0

    for entity in cluster:

        if str(entity).startswith("dispute_"):
            dispute_count += 1

        if str(entity).startswith("tx_"):
            transaction_count += 1

    if transaction_count == 0:
        return 0

    dispute_ratio = dispute_count / transaction_count

    score = min(dispute_ratio * 1.5, 1)

    return round(score, 3)
