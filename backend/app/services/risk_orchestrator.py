from datetime import datetime


class RiskOrchestrator:
    """
    Central fraud intelligence orchestrator.

    Coordinates multiple fraud detection engines
    and aggregates their outputs into a unified risk profile.

    Engines may include:

    - rule based fraud signals
    - device fingerprint intelligence
    - ML chargeback prediction
    - fraud graph cluster detection
    - cross merchant intelligence
    """

    def __init__(self, engines):
        self.engines = engines

    def evaluate(self, context: dict):
        """
        Runs all fraud engines and aggregates their outputs.

        Parameters
        ----------
        context : dict
            transaction context including device, merchant, user

        Returns
        -------
        dict
            unified fraud evaluation result
        """

        results = {}
        total_score = 0
        weight_sum = 0

        for engine in self.engines:
            name = engine.__class__.__name__

            try:
                result = engine.evaluate(context)

                results[name] = result

                if isinstance(result, dict) and "score" in result:
                    weight = result.get("weight", 1)
                    total_score += result["score"] * weight
                    weight_sum += weight

            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e)
                }

        final_score = 0
        if weight_sum > 0:
            final_score = total_score / weight_sum

        risk_level = "low"

        if final_score > 0.75:
            risk_level = "critical"
        elif final_score > 0.55:
            risk_level = "high"
        elif final_score > 0.35:
            risk_level = "medium"

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "risk_score": round(final_score, 4),
            "risk_level": risk_level,
            "engine_results": results
        }