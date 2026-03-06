from sqlalchemy.orm import Session
from app.models.fraud_signal import FraudSignal


def store_fraud_signal(db: Session, transaction_id: str, signal_type: str, description: str):

    signal = FraudSignal(
        transaction_id=transaction_id,
        signal_type=signal_type,
        description=description
    )

    db.add(signal)
    db.commit()
    db.refresh(signal)

    return signal
