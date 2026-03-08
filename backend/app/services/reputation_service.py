from sqlalchemy.orm import Session
from app.models.reputation import Reputation


def update_reputation(db: Session, entity_type: str, entity_id: str, is_dispute: bool = False):
    """
    Update the reputation score for a given entity.
    Entities can be: device, customer, email, ip, merchant, etc.
    """

    record = (
        db.query(Reputation)
        .filter(
            Reputation.entity_type == entity_type,
            Reputation.entity_id == entity_id
        )
        .first()
    )

    # Create record if it doesn't exist
    if not record:
        record = Reputation(
            entity_type=entity_type,
            entity_id=entity_id,
            total_transactions=0,
            total_disputes=0,
            reputation_score=0
        )
        db.add(record)

    # Update transaction counter
    record.total_transactions += 1

    # Update dispute counter
    if is_dispute:
        record.total_disputes += 1

    # Calculate reputation score
    if record.total_transactions > 0:
        dispute_ratio = record.total_disputes / record.total_transactions
    else:
        dispute_ratio = 0

    # Reputation scoring heuristic
    record.reputation_score = min(dispute_ratio * 1.5, 1)

    db.commit()

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "reputation_score": record.reputation_score,
        "transactions": record.total_transactions,
        "disputes": record.total_disputes
    }


def get_reputation(db: Session, entity_type: str, entity_id: str):
    """
    Retrieve reputation data for an entity.
    """

    record = (
        db.query(Reputation)
        .filter(
            Reputation.entity_type == entity_type,
            Reputation.entity_id == entity_id
        )
        .first()
    )

    if not record:
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "reputation_score": 0,
            "transactions": 0,
            "disputes": 0
        }

    return {
        "entity_type": record.entity_type,
        "entity_id": record.entity_id,
        "reputation_score": record.reputation_score,
        "transactions": record.total_transactions,
        "disputes": record.total_disputes
    }