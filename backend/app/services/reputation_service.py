from app.models.reputation import Reputation


def update_reputation(db, entity_type, entity_id, is_dispute=False):

    record = (
        db.query(Reputation)
        .filter(
            Reputation.entity_type == entity_type,
            Reputation.entity_id == entity_id
        )
        .first()
    )

    if not record:
        record = Reputation(
            entity_type=entity_type,
            entity_id=entity_id,
            total_transactions=0,
            total_disputes=0
        )
        db.add(record)

    record.total_transactions += 1

    if is_dispute:
        record.total_disputes += 1

    dispute_ratio = record.total_disputes / record.total_transactions

    record.reputation_score = min(dispute_ratio * 1.5, 1)

    db.commit()

    return record.reputation_score