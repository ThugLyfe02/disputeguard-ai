from sqlalchemy.orm import Session
from datetime import datetime

from app.models.fraud_features import FraudFeature


"""
Feature Store

This module stores and retrieves fraud intelligence features.

These features are used by:

• Rule engines
• ML models
• Fraud graph analysis
• Reputation scoring
• Cross-merchant intelligence

Feature Store Design Goals:

1. Persist fraud intelligence signals
2. Enable ML model training
3. Enable real-time feature retrieval
4. Provide historical datasets
"""


# --------------------------------------------------------
# STORE FEATURES
# --------------------------------------------------------

def store_features(
    db: Session,
    transaction_id: str,
    merchant_id: str,
    amount: float,
    rule_score: float,
    device_risk_score: float,
    reputation_score: float,
    cluster_risk_score: float,
    chargeback_probability: float
):
    """
    Persist fraud signals for a transaction.

    This becomes training data for ML models
    and intelligence signals for fraud detection.
    """

    feature = FraudFeature(
        transaction_id=transaction_id,
        merchant_id=merchant_id,
        amount=amount,
        rule_score=rule_score,
        device_risk_score=device_risk_score,
        reputation_score=reputation_score,
        cluster_risk_score=cluster_risk_score,
        chargeback_probability=chargeback_probability,
        created_at=datetime.utcnow()
    )

    db.add(feature)
    db.commit()
    db.refresh(feature)

    return feature


# --------------------------------------------------------
# GET FEATURES FOR A TRANSACTION
# --------------------------------------------------------

def get_transaction_features(db: Session, transaction_id: str):
    """
    Retrieve stored fraud signals for a transaction.
    """

    feature = (
        db.query(FraudFeature)
        .filter(FraudFeature.transaction_id == transaction_id)
        .first()
    )

    if not feature:
        return None

    return {
        "transaction_id": feature.transaction_id,
        "merchant_id": feature.merchant_id,
        "amount": feature.amount,
        "rule_score": feature.rule_score,
        "device_risk_score": feature.device_risk_score,
        "reputation_score": feature.reputation_score,
        "cluster_risk_score": feature.cluster_risk_score,
        "chargeback_probability": feature.chargeback_probability
    }


# --------------------------------------------------------
# BUILD TRAINING DATASET
# --------------------------------------------------------

def get_training_data(db: Session):
    """
    Build ML training dataset from stored fraud features.
    """

    records = db.query(FraudFeature).all()

    dataset = []

    for r in records:
        dataset.append({
            "amount": r.amount,
            "rule_score": r.rule_score,
            "device_risk_score": r.device_risk_score,
            "reputation_score": r.reputation_score,
            "cluster_risk_score": r.cluster_risk_score,
            "label": r.chargeback_probability
        })

    return dataset


# --------------------------------------------------------
# MERCHANT FEATURE AGGREGATION
# --------------------------------------------------------

def get_merchant_feature_stats(db: Session, merchant_id: str):
    """
    Aggregate merchant fraud intelligence.
    """

    records = (
        db.query(FraudFeature)
        .filter(FraudFeature.merchant_id == merchant_id)
        .all()
    )

    if not records:
        return {
            "merchant_id": merchant_id,
            "transactions": 0,
            "avg_rule_score": 0,
            "avg_device_risk": 0,
            "avg_cluster_risk": 0
        }

    count = len(records)

    avg_rule = sum(r.rule_score for r in records) / count
    avg_device = sum(r.device_risk_score for r in records) / count
    avg_cluster = sum(r.cluster_risk_score for r in records) / count

    return {
        "merchant_id": merchant_id,
        "transactions": count,
        "avg_rule_score": round(avg_rule, 3),
        "avg_device_risk": round(avg_device, 3),
        "avg_cluster_risk": round(avg_cluster, 3)
    }


# --------------------------------------------------------
# GLOBAL FRAUD INTELLIGENCE
# --------------------------------------------------------

def global_fraud_summary(db: Session):
    """
    Global fraud intelligence across all merchants.
    """

    records = db.query(FraudFeature).all()

    if not records:
        return {
            "total_transactions": 0,
            "avg_chargeback_probability": 0
        }

    total = len(records)

    avg_prob = sum(r.chargeback_probability for r in records) / total

    return {
        "total_transactions": total,
        "avg_chargeback_probability": round(avg_prob, 3)
    }