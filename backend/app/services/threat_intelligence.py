from app.models.threat_indicator import ThreatIndicator


def lookup_threat_indicator(db, indicator_type, indicator_value):

    record = (
        db.query(ThreatIndicator)
        .filter(
            ThreatIndicator.indicator_type == indicator_type,
            ThreatIndicator.indicator_value == indicator_value
        )
        .first()
    )

    if not record:
        return {
            "indicator_type": indicator_type,
            "indicator_value": indicator_value,
            "threat_level": 0
        }

    return {
        "indicator_type": record.indicator_type,
        "indicator_value": record.indicator_value,
        "threat_level": record.threat_level,
        "source": record.source
    }