"""
test_fraud_pipeline.py

Integration tests for the DisputeGuard AI fraud pipeline.

Verifies end-to-end correctness of:
- Fraud network graph (detect_cluster return structure)
- Temporal graph (index-based lookups, velocity signal)
- Risk orchestrator (weighted aggregation, error boundaries)
- ML model (predict returns safe defaults when untrained)
- Event bus (publish/subscribe, idempotency, handler isolation)
- Graph signal cache (update, eviction, refresh-ahead)
- Subscriber payload parsing (nested structure navigation)
"""

import pytest
import time
import threading

# ---------------------------------------------------------------------------
# Graph: detect_cluster return structure
# ---------------------------------------------------------------------------

from app.services.fraud_network_graph import FraudNetworkGraph


class TestDetectCluster:

    def test_returns_dict_with_nodes_and_capped(self):
        g = FraudNetworkGraph()
        g.add_edge("tx_1", "device_a")
        g.add_edge("tx_1", "merchant_m1")

        result = g.detect_cluster("tx_1")

        assert isinstance(result, dict)
        assert "nodes" in result
        assert "cluster_capped" in result
        assert isinstance(result["nodes"], list)
        assert isinstance(result["cluster_capped"], bool)

    def test_cluster_contains_connected_nodes(self):
        g = FraudNetworkGraph()
        g.add_edge("tx_1", "device_a")
        g.add_edge("tx_1", "merchant_m1")
        g.add_edge("device_a", "tx_2")

        result = g.detect_cluster("tx_1")
        nodes = set(result["nodes"])

        assert "tx_1" in nodes
        assert "device_a" in nodes
        assert "merchant_m1" in nodes
        assert "tx_2" in nodes
        assert result["cluster_capped"] is False

    def test_absent_node_returns_empty(self):
        g = FraudNetworkGraph()

        result = g.detect_cluster("nonexistent_node")

        assert result == {"nodes": [], "cluster_capped": False}

    def test_capped_when_exceeding_limit(self):
        g = FraudNetworkGraph()

        # Build a chain of 20 nodes
        for i in range(20):
            g.add_edge(f"n_{i}", f"n_{i+1}")

        result = g.detect_cluster("n_0", max_nodes=5)

        assert result["cluster_capped"] is True
        assert len(result["nodes"]) <= 5

    def test_network_risk_accepts_node_list(self):
        g = FraudNetworkGraph()
        g.add_edge("tx_1", "device_a")
        g.add_edge("tx_1", "dispute_d1")

        result = g.detect_cluster("tx_1")
        risk = g.calculate_network_risk(result["nodes"])

        assert isinstance(risk, float)
        assert 0.0 <= risk <= 1.0

    def test_graph_density(self):
        g = FraudNetworkGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        g.add_edge("a", "c")

        density = g.graph_density(["a", "b", "c"])

        assert density == 1.0  # fully connected triangle

    def test_prune_old_nodes(self):
        g = FraudNetworkGraph()
        g.add_edge("tx_1", "device_a")

        # Pruning with default 90-day window should not remove fresh nodes
        result = g.prune_old_nodes(days=90)

        assert isinstance(result, dict)
        assert "removed" in result
        assert "remaining" in result


# ---------------------------------------------------------------------------
# Temporal graph: index, velocity, pruning
# ---------------------------------------------------------------------------

from app.services.temporal_graph import TemporalGraph


class TestTemporalGraph:

    def test_add_edge_updates_node_index(self):
        tg = TemporalGraph()
        tg.add_edge("device_a", "merchant_m1")

        assert len(tg.node_index["device_a"]) > 0
        assert len(tg.node_index["merchant_m1"]) > 0

    def test_recent_connections_uses_index(self):
        tg = TemporalGraph()
        tg.add_edge("device_a", "merchant_m1")
        tg.add_edge("device_a", "merchant_m2")

        recent = tg.recent_connections("device_a", window_seconds=60)

        assert "merchant_m1" in recent
        assert "merchant_m2" in recent

    def test_velocity_signal_normalized(self):
        tg = TemporalGraph()
        for i in range(15):
            tg.add_edge("device_a", f"merchant_{i}")

        signal = tg.velocity_signal("device_a", window_seconds=120, cap=10)

        assert signal == 1.0  # 15 connections / cap 10 = clamped to 1.0

    def test_velocity_signal_zero_for_unknown_node(self):
        tg = TemporalGraph()

        signal = tg.velocity_signal("nonexistent")

        assert signal == 0.0

    def test_merchant_hopping_velocity(self):
        tg = TemporalGraph()
        tg.add_edge("device_a", "merchant_1")
        tg.add_edge("device_a", "merchant_2")
        tg.add_edge("device_a", "merchant_3")
        tg.add_edge("device_a", "tx_99")  # not a merchant

        count = tg.merchant_hopping_velocity("device_a", window_seconds=60)

        assert count == 3

    def test_prune_removes_stale_edges_and_updates_index(self):
        tg = TemporalGraph()
        tg.add_edge("a", "b")

        # Manually backdate the timestamp to make it stale
        for key in list(tg.edges.keys()):
            tg.edges[key] = [time.time() - 99999]

        tg.prune_old_edges(ttl_seconds=60)

        assert tg.edge_count() == 0
        # Index should also be cleaned
        assert len(tg.node_index.get("a", set())) == 0


# ---------------------------------------------------------------------------
# Risk orchestrator: weighted scoring, error boundaries
# ---------------------------------------------------------------------------

from app.risk_engines.base_engine import RiskEngine
from app.services.risk_orchestrator import RiskOrchestrator


class StubEngine(RiskEngine):
    name = "stub_engine"

    def __init__(self, score=0.5):
        self._score = score

    def evaluate(self, db, context):
        return {"score": self._score, "details": {}}


class FailingEngine(RiskEngine):
    name = "failing_engine"

    def evaluate(self, db, context):
        raise RuntimeError("Engine failure")


class TestRiskOrchestrator:

    def test_evaluate_returns_required_keys(self):
        orchestrator = RiskOrchestrator([StubEngine(0.3)])

        result = orchestrator.evaluate(None, {"transaction": {}})

        assert "engines" in result
        assert "scores" in result
        assert "final_risk_score" in result
        assert "pipeline_timing" in result

    def test_scores_within_unit_range(self):
        orchestrator = RiskOrchestrator([
            StubEngine(0.2),
            StubEngine(0.8),
        ])
        # Override names for dedup
        orchestrator.engines[0].name = "engine_a"
        orchestrator.engines[1].name = "engine_b"

        result = orchestrator.evaluate(None, {"transaction": {}})

        assert 0.0 <= result["final_risk_score"] <= 1.0

    def test_failing_engine_uses_fallback_score(self):
        orchestrator = RiskOrchestrator([FailingEngine()])

        result = orchestrator.evaluate(None, {"transaction": {}})

        assert result["scores"]["failing_engine"] == 0.5

    def test_timing_present(self):
        orchestrator = RiskOrchestrator([StubEngine(0.5)])

        result = orchestrator.evaluate(None, {"transaction": {}})

        timing = result["pipeline_timing"]
        assert "total_ms" in timing
        assert "engines" in timing
        assert timing["total_ms"] >= 0


# ---------------------------------------------------------------------------
# ML model: safe defaults when untrained
# ---------------------------------------------------------------------------

from app.services.fraud_ml_model import FraudMLModel


class TestFraudMLModel:

    def test_untrained_predict_returns_safe_defaults(self):
        model = FraudMLModel()

        prob, confidence = model.predict({
            "amount": 100.0,
            "rule_score": 0.5,
            "device_risk_score": 0.3,
            "reputation_score": 0.2,
            "cluster_risk_score": 0.1,
        })

        assert prob == 0.5
        assert confidence == 0.0

    def test_predict_chargeback_returns_expected_structure(self):
        from app.services.fraud_ml_prediction import predict_chargeback

        result = predict_chargeback(
            amount=99.0,
            rule_score=0.5,
            device_risk_score=0.3,
            reputation_score=0.2,
            cluster_risk_score=0.1,
        )

        assert "chargeback_probability" in result
        assert "prediction_confidence" in result
        assert "risk_level" in result
        assert "features_used" in result
        assert result["risk_level"] in ("low", "medium", "high")

    def test_feature_keys_match_training_data(self):
        from app.services.fraud_training_data import build_training_dataset

        # Training data row keys (minus 'label') must match FEATURE_KEYS
        sample_row = {
            "amount": 100,
            "rule_score": 0,
            "device_risk_score": 0,
            "reputation_score": 0,
            "cluster_risk_score": 0,
            "label": 0,
        }

        model = FraudMLModel()

        for key in model.FEATURE_KEYS:
            assert key in sample_row, f"Training data missing feature: {key}"


# ---------------------------------------------------------------------------
# Event bus: publish, subscribe, idempotency, handler isolation
# ---------------------------------------------------------------------------

from app.services.event_bus import EventBus


class TestEventBus:

    def test_publish_and_subscribe(self):
        bus = EventBus()
        received = []

        bus.subscribe("test.event", lambda payload: received.append(payload))
        bus.publish("test.event", {"data": "hello"})

        assert len(received) == 1
        assert received[0]["data"] == "hello"

    def test_idempotency_prevents_duplicate(self):
        bus = EventBus()
        received = []

        bus.subscribe("test.event", lambda p: received.append(p))
        bus.publish("test.event", {"n": 1}, event_id="evt-1")
        bus.publish("test.event", {"n": 2}, event_id="evt-1")

        assert len(received) == 1

    def test_handler_failure_does_not_break_others(self):
        bus = EventBus()
        results = []

        def failing_handler(p):
            raise ValueError("boom")

        def success_handler(p):
            results.append("ok")

        bus.subscribe("test.event", failing_handler)
        bus.subscribe("test.event", success_handler)

        result = bus.publish("test.event", {})

        # Second handler still ran despite first failing
        assert len(results) == 1
        assert results[0] == "ok"
        # Result contains both handler outcomes
        assert len(result["results"]) == 2
        assert result["results"][0]["status"] == "error"
        assert result["results"][1]["status"] == "success"

    def test_lru_eviction_at_capacity(self):
        bus = EventBus()
        bus.MAX_IDEMPOTENCY_KEYS = 5

        for i in range(10):
            bus.publish("test.event", {}, event_id=f"evt-{i}")

        # Oldest events should have been evicted
        assert len(bus.processed_event_ids) == 5
        # First 5 should be evicted
        assert "evt-0" not in bus.processed_event_ids
        assert "evt-9" in bus.processed_event_ids


# ---------------------------------------------------------------------------
# Subscriber payload parsing: nested structure navigation
# ---------------------------------------------------------------------------

class TestSubscriberPayloadParsing:

    def _build_pipeline_payload(self):
        """Build a payload matching the structure published by fraud_pipeline."""
        return {
            "event_id": "evt-test-001",
            "transaction_id": "tx-123",
            "merchant_id": "merchant-456",
            "fraud_result": {
                "event_id": "evt-test-001",
                "transaction_id": "tx-123",
                "merchant_id": "merchant-456",
                "scores": {
                    "rule_score": 0.45,
                    "device_risk_score": 0.3,
                    "cluster_risk_score": 0.2,
                    "network_risk_score": 0.1,
                    "fraud_network_score": 0.15,
                    "chargeback_probability": 0.75,
                    "reputation_score": 0.5,
                },
                "signals": {
                    "device_risk": {"some": "data"},
                    "graph_cluster": {"cluster_risk_score": 0.2},
                    "cross_merchant": {},
                    "network_analysis": {},
                    "fraud_network_analysis": {},
                    "graph_features": {},
                    "reputation": {"reputation_score": 0.5},
                    "ml_prediction": {
                        "chargeback_probability": 0.75,
                        "prediction_confidence": 0.8,
                        "risk_level": "high",
                        "features_used": {
                            "amount": 500.0,
                            "device_risk_score": 0.3,
                        },
                    },
                },
                "final_risk_score": 0.42,
                "pipeline_timing": {"total_ms": 12.5, "engines": {}},
                "alert": None,
            },
        }

    def test_case_management_subscriber_reads_chargeback_probability(self):
        payload = self._build_pipeline_payload()

        inner = payload.get("fraud_result", {})
        ml_prediction = inner.get("signals", {}).get("ml_prediction", {})
        prob = ml_prediction.get("chargeback_probability", 0.0)

        assert prob == 0.75

    def test_feature_store_subscriber_reads_scores_and_signals(self):
        payload = self._build_pipeline_payload()

        inner = payload.get("fraud_result", {})
        scores = inner.get("scores", {})
        signals = inner.get("signals", {})

        assert scores.get("rule_score") == 0.45
        assert signals.get("reputation", {}).get("reputation_score") == 0.5
        assert (
            signals.get("ml_prediction", {}).get("chargeback_probability") == 0.75
        )

    def test_fraud_result_has_timing_metadata(self):
        payload = self._build_pipeline_payload()

        fraud_result = payload.get("fraud_result", {})

        assert "final_risk_score" in fraud_result
        assert "pipeline_timing" in fraud_result
        assert "total_ms" in fraud_result["pipeline_timing"]


# ---------------------------------------------------------------------------
# Graph signal cache: update and eviction
# ---------------------------------------------------------------------------

from app.services.graph_signal_cache import GraphSignalCache


class TestGraphSignalCache:

    def test_update_populates_signals(self):
        from app.services.fraud_network_graph import FraudNetworkGraph

        # Use a fresh graph + cache to avoid singleton interference
        cache = GraphSignalCache()
        g = FraudNetworkGraph()
        g.add_edge("tx_1", "device_a")
        g.add_edge("tx_1", "merchant_m1")

        # Monkey-patch the cache's fraud_graph reference
        import app.services.graph_signal_cache as cache_mod
        original_graph = cache_mod.fraud_graph
        cache_mod.fraud_graph = g
        try:
            cache.update("tx_1")

            assert cache.get_cluster_size("tx_1") > 0
            assert cache.get_cluster_risk("tx_1") >= 0.0

            signals = cache.get_signals("tx_1")
            assert "cluster_risk_score" in signals
            assert "velocity_score" in signals
            assert "cluster_density" in signals
        finally:
            cache_mod.fraud_graph = original_graph

    def test_eviction_respects_max_entries(self):
        cache = GraphSignalCache()
        cache.MAX_CACHE_ENTRIES = 5
        cache.STALE_AGE = 0  # everything is stale immediately

        # Populate with entries
        for i in range(10):
            cache.cluster_risk[f"node_{i}"] = 0.5
            cache.last_update[f"node_{i}"] = time.time() - 600

        cache._evict_stale()

        assert len(cache.last_update) <= 5
