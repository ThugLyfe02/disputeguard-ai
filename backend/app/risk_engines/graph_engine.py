"""
graph_engine.py — Fraud graph cluster analysis engine.

Wraps :func:`app.services.fraud_graph_analysis.analyze_entity_cluster` to
surface entity-cluster-based fraud signals within the plugin-based pipeline.

The engine uses the ``device_hash`` from the shared evaluation context as the
graph entity identifier and returns the cluster's fraud risk score alongside
the full cluster diagnostic payload.

Example::

    from app.risk_engines.graph_engine import GraphEngine

    engine = GraphEngine()
    result = engine.evaluate(db, context)
    # result == {
    #     "score": 0.6,
    #     "details": {
    #         "entity": "abc123",
    #         "cluster_size": 4,
    #         "cluster_entities": [...],
    #         "cluster_risk_score": 0.6
    #     }
    # }
"""

from app.risk_engines.base_engine import RiskEngine
from app.services.fraud_graph_analysis import analyze_entity_cluster


class GraphEngine(RiskEngine):
    """
    Fraud risk engine based on graph cluster analysis.

    Delegates to :func:`~app.services.fraud_graph_analysis.analyze_entity_cluster`
    to build a fraud relationship graph, detect the cluster connected to the
    device entity, and score the cluster's collective fraud risk.

    Attributes
    ----------
    name : str
        Engine identifier — ``"graph_engine"``.
    """

    name = "graph_engine"

    def evaluate(self, db, context: dict) -> dict:
        """
        Analyse the fraud cluster associated with the device entity.

        Parameters
        ----------
        db : sqlalchemy.orm.Session
            Active database session forwarded to the underlying service.
        context : dict
            Orchestrator evaluation context.  Must contain:

            * ``"device_hash"`` (str | None) — device fingerprint hash used
              as the graph entity identifier.

        Returns
        -------
        dict
            * ``"score"`` (float) — cluster risk score in ``[0, 1]`` as
              computed by the fraud ring scorer.
            * ``"details"`` (dict) — full payload returned by
              :func:`~app.services.fraud_graph_analysis.analyze_entity_cluster`,
              including ``cluster_size`` and ``cluster_entities``.
        """
        device_hash = context.get("device_hash")

        result = analyze_entity_cluster(db, device_hash)

        return {
            "score": float(result.get("cluster_risk_score", 0.0)),
            "details": result,
        }
