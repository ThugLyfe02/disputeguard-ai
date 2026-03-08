from app.models.incident_event import IncidentEvent


def add_event(db, incident_id, event_type, entity_id):

    event = IncidentEvent(
        incident_id=incident_id,
        event_type=event_type,
        entity_id=entity_id
    )

    db.add(event)
    db.commit()

    return event


def get_timeline(db, incident_id):

    events = (
        db.query(IncidentEvent)
        .filter(IncidentEvent.incident_id == incident_id)
        .all()
    )

    return [
        {
            "event_type": e.event_type,
            "entity": e.entity_id,
            "timestamp": e.timestamp
        }
        for e in events
    ]