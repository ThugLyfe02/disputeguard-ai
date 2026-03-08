from app.models.threat_indicator import ThreatIndicator


def ingest_indicator(db, indicator_type, indicator_value, threat_level, source):

    indicator = ThreatIndicator(
        indicator_type=indicator_type,
        indicator_value=indicator_value,
        threat_level=threat_level,
        source=source
    )

    db.add(indicator)
    db.commit()

    return indicator