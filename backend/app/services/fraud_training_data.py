from app.models.transaction import Transaction
from app.models.dispute import Dispute


def build_training_dataset(db):

    dataset = []

    transactions = db.query(Transaction).all()

    for tx in transactions:

        dispute = db.query(Dispute).filter(
            Dispute.transaction_id == tx.id
        ).first()

        label = 1 if dispute else 0

        dataset.append({
            "amount": tx.amount,
            "rule_score": 0,
            "device_risk_score": 0,
            "reputation_score": 0,
            "cluster_risk_score": 0,
            "label": label
        })

    return dataset
