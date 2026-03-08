from app.models.fraud_incident import FraudIncident


def create_incident(db, incident_type, severity, entity_id):

    incident = FraudIncident(
        incident_type=incident_type,
        severity=severity,
        entity_id=entity_id
    )

    db.add(incident)
    db.commit()

    return incident