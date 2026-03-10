# DisputeGuard AI — Architectural Review & Surgical Fix Plan

**Review type**: Production readiness audit
**Scope**: Full backend pipeline, risk engines, graph intelligence, event system, subscribers, frontend
**Approach**: Verify prior findings against actual code, eliminate false positives, produce minimal high-impact fix plan

---

## 1. Verified Findings

Each finding from the prior audit was traced to exact lines in the codebase. Below is the verification result.

---

### BUG-1: Score Scale Mismatch in Orchestrator [CONFIRMED CRITICAL]

**Root cause**: `RuleEngine` returns raw additive integers. All other engines return `[0, 1]`.

**Evidence chain**:

- `fraud_signals.py:7` — `risk_score = 0`, then `+= 30` (line 13), `+= 25` (line 26). Max possible return: **55**.
- `rule_engine.py:67` — `"score": float(score)` — passes raw integer through unchanged.
- `risk_orchestrator.py:138-141` — `sum(scores.values()) / len(scores)` — arithmetic mean of all 8 engine scores.

**Failure mode**: With 8 engines, if RuleEngine returns 55 and all others return ~0.3, the mean is `(55 + 7*0.3) / 8 = 7.1`. This exceeds `[0, 1]` by 7x, making `final_risk_score` meaningless for thresholding.

**Downstream impact**: `generate_alert()` in `fraud_alerts.py` likely uses `final_risk_score` for alert thresholds. Any threshold calibrated for `[0, 1]` will always trigger when RuleEngine fires.

**Fix**: Normalize in `rule_engine.py` — divide by 100 (the maximum possible score). One-line change. Does not break any consumers since the orchestrator and MLEngine already treat it as a float.

```python
# rule_engine.py:67 — change:
"score": float(score),
# to:
"score": min(float(score) / 100.0, 1.0),
```

---

### BUG-2: ML Model Signature Mismatch [CONFIRMED CRITICAL]

**Root cause**: `predict_chargeback()` passes a dict to `model.predict()`, but `FraudMLModel.predict()` expects two positional args.

**Evidence chain**:

- `fraud_ml_prediction.py:47-53` — builds `features = {"amount": ..., "rule_score": ..., ...}` (5-key dict)
- `fraud_ml_prediction.py:55` — calls `model.predict(features)` — passes dict as single arg
- `fraud_ml_model.py:28` — `def predict(self, amount, signal_count)` — expects 2 positional args

**Failure mode**: `TypeError: predict() missing 1 required positional argument: 'signal_count'` on every call. The ML engine crashes every time the pipeline runs.

**Secondary issue**: Even if the signature matched, the model trains on 2 features (`amount`, `signal_count`) but prediction passes 5 different features. Dimensionality mismatch would cause sklearn to raise `ValueError`.

**Fix**: Align the `predict()` method to accept the feature dict and extract what it needs. Also align training to use the same 5 features so the model can actually leverage upstream engine signals.

```python
# fraud_ml_model.py — fix predict() to accept feature dict:
def predict(self, features: dict):
    amount = features.get("amount", 0)
    rule_score = features.get("rule_score", 0)
    device_risk_score = features.get("device_risk_score", 0)
    reputation_score = features.get("reputation_score", 0)
    cluster_risk_score = features.get("cluster_risk_score", 0)

    X = np.array([[amount, rule_score, device_risk_score, reputation_score, cluster_risk_score]])

    try:
        probability = self.model.predict_proba(X)[0][1]
    except Exception:
        return 0.5  # untrained model fallback

    return round(float(probability), 3)
```

Training alignment is also required — `train()` must use the same 5 features. But this is a data pipeline issue that requires training data restructuring, so it should be a separate task.

---

### BUG-3: Subscriber Payload Mismatch [CONFIRMED CRITICAL]

**Root cause**: Subscribers expect flat top-level keys but the pipeline publishes a nested structure.

**Evidence chain**:

The pipeline publishes this payload at `fraud_pipeline.py:230-234`:
```python
event_payload = {
    "event_id": event_id,
    "transaction_id": transaction_id,
    "merchant_id": merchant_id,
    "fraud_result": fraud_result  # nested dict with "scores", "signals" sub-dicts
}
```

But subscribers read flat keys:

- `case_management_subscriber.py:50` — `fraud_result.get("ml_prediction", {})` — expects `ml_prediction` at top level. Actual location: `fraud_result["fraud_result"]["signals"]["ml_prediction"]`.
- `feature_store_subscriber.py:54` — `fraud_result.get("rule_score", 0.0)` — expects `rule_score` at top level. Actual location: `fraud_result["fraud_result"]["scores"]["rule_score"]`.
- `feature_store_subscriber.py:56` — `fraud_result.get("ml_prediction", {})` — same issue.
- `feature_store_subscriber.py:62` — `fraud_result.get("reputation", {})` — actual location: `fraud_result["fraud_result"]["signals"]["reputation"]`.
- `feature_store_subscriber.py:65` — `fraud_result.get("graph_cluster", {})` — actual location: `fraud_result["fraud_result"]["signals"]["graph_cluster"]`.

**Failure mode**: All `.get()` calls return defaults (`{}` or `0.0`). Case management never creates fraud cases (chargeback_probability is always 0.0). Feature store always stores zeroed-out features, corrupting the ML training dataset.

**Impact**: The entire downstream event system is non-functional. Events fire, handlers execute, but they operate on empty data.

**Fix**: Subscribers need to navigate the nested structure. Extract `fraud_result["fraud_result"]` first, then access `["signals"]` and `["scores"]`.

```python
# case_management_subscriber.py:48 — add:
inner_result = fraud_result.get("fraud_result", {})
ml_prediction = inner_result.get("signals", {}).get("ml_prediction", {})

# feature_store_subscriber.py:52 — add:
inner_result = fraud_result.get("fraud_result", {})
scores = inner_result.get("scores", {})
signals = inner_result.get("signals", {})
rule_score = scores.get("rule_score", 0.0)
ml_prediction = signals.get("ml_prediction", {})
reputation = signals.get("reputation", {})
graph_cluster = signals.get("graph_cluster", {})
```

---

### BUG-4: Double Temporal Edge Recording [CONFIRMED]

**Evidence chain**:

- `fraud_pipeline.py:88-89` — explicitly calls `temporal_graph.add_edge(tx_node, device_node)` and `temporal_graph.add_edge(tx_node, merchant_node)`.
- `fraud_pipeline.py:78-82` — calls `fraud_graph.build_graph_from_transaction(transaction, device_hash, merchant_id)`.
- `fraud_network_graph.py:226-227` — `build_graph_from_transaction` calls `self.add_edge(tx_node, device_node)` and `self.add_edge(tx_node, merchant_node)`.
- `fraud_network_graph.py:156` — `add_edge()` calls `temporal_graph.add_edge(node_a, node_b)`.

**Result**: `temporal_graph.add_edge()` is called **twice** for each `(tx, device)` and `(tx, merchant)` pair. Each call records both `(a,b)` and `(b,a)` directions, so the actual inflation is **4x** temporal entries per core edge instead of 2x.

**Impact**: Velocity scores (`connection_velocity`) are inflated 2x. Burst detection thresholds are effectively halved. Any velocity-based risk signal is systematically overstated.

**Fix**: Remove lines 88-89 from `fraud_pipeline.py`. The fraud graph already records temporal edges internally.

---

### PERF-1: O(E) Temporal Graph Queries [CONFIRMED]

**Evidence**: `temporal_graph.py:76` — `for (a, b), timestamps in self.edges.items()` scans the entire edge dict to find connections for a single node.

**Impact**: Every call to `connection_velocity()` or `recent_connections()` is O(E) where E = total temporal edges. With `calculate_network_risk()` calling `connection_velocity()` for every node in a cluster (`fraud_network_graph.py:370`), and `graph_signal_cache.py:121` doing the same for every node in a cluster, this compounds to O(C * E) per signal cache update where C = cluster size.

**Fix**: Add a node-to-edge-keys index. One new `defaultdict(set)` in `__init__`, updated in `add_edge`, queried in `recent_connections`.

```python
# In __init__:
self.node_index = defaultdict(set)  # node -> set of (node_a, node_b) keys

# In add_edge, after existing lines 58-59:
self.node_index[node_a].add((node_a, node_b))
self.node_index[node_b].add((node_b, node_a))

# Replace recent_connections body:
def recent_connections(self, node, window_seconds=120):
    now = datetime.utcnow().timestamp()
    neighbors = []
    with self._lock:
        for key in self.node_index.get(node, set()):
            timestamps = self.edges.get(key, [])
            if any(now - t <= window_seconds for t in timestamps):
                neighbors.append(key[1])
    return neighbors
```

This changes the query from O(E) to O(degree(node)), which is typically orders of magnitude smaller.

---

### PERF-2: Unbounded Memory Growth [CONFIRMED]

**Affected modules**:

| Module | Data structure | Growth pattern |
|--------|---------------|----------------|
| `fraud_network_graph.py` | `self.graph: defaultdict(set)` | Never pruned. Every transaction adds ≥3 nodes + ≥2 edges. |
| `temporal_graph.py` | `self.edges: defaultdict(list)` | `prune_old_edges()` exists but is never called. |
| `graph_signal_cache.py` | 6x `defaultdict` + `last_update` dict | Entries never evicted. |
| `event_bus.py:94` | `self.processed_event_ids: set` | Grows with every event, never bounded. |

**Fix**: Wire `temporal_graph.prune_old_edges()` to a periodic task. For the event bus, cap `processed_event_ids` using a bounded deque or LRU. For the fraud graph and signal cache, add TTL-based pruning as a background task.

Minimal immediate fix for event bus memory leak:

```python
# event_bus.py — change processed_event_ids from set to bounded:
from collections import deque

# In __init__:
self.processed_event_ids = deque(maxlen=50000)

# In publish — change "in set" check to:
if event_id in set(self.processed_event_ids):
```

Note: Converting deque to set for lookup is O(N). A proper LRU is better but this prevents unbounded growth immediately.

---

### PERF-3: Synchronous Event Handlers [CONFIRMED]

**Evidence**: `event_bus.py:107-126` — handlers execute synchronously in the publisher's thread.

**Specific concern**: `fraud_network_subscriber.py:56` — `build_fraud_network(db)` rebuilds the entire fraud network graph from the database on every `fraud.analysis.completed` event. This is a full table scan + graph construction, blocking the fraud pipeline response.

**Severity**: Medium. For low throughput this is acceptable. For high throughput this becomes a bottleneck. The fix is straightforward (thread pool or async dispatch) but should not be done prematurely.

**Recommendation**: Mark as **FUTURE**. The current synchronous model is simpler to reason about and debug. Convert to async dispatch only when pipeline latency SLA is violated.

---

## 2. False Positives & Over-Engineering from Prior Audit

### FALSE POSITIVE: "No error boundaries in pipeline"

The prior audit noted the pipeline has no try/except. This is partially true but the **risk is overstated**. Each engine runs via the orchestrator's `for engine in self.engines` loop (`risk_orchestrator.py:131-134`). If one engine throws, the entire orchestrator fails — but the pipeline at `fraud_pipeline.py:126` does call the orchestrator as a single unit.

**Nuance**: Adding per-engine try/except in the orchestrator is reasonable but introduces a design question: should a transaction get a risk score based on partial engine results? In fraud systems, a missing signal is often more dangerous than a failed evaluation. Silently swallowing an engine failure could produce a falsely low risk score, allowing a fraudulent transaction through.

**Recommendation**: Add per-engine error handling, but when an engine fails, set its score to a **configurable default** (e.g., 0.5 — "uncertain") rather than 0.0 ("safe"). Log the failure prominently.

### OVER-ENGINEERING: Kafka / Neo4j / Redis recommendations

The prior audit recommended Kafka, Neo4j, and Redis. These are all valid at scale but **premature for the current stage**.

- **Kafka**: The in-memory event bus handles the current throughput. Kafka adds operational complexity (ZooKeeper/KRaft, topic management, consumer groups, offset management). Only justified when: (a) events must survive process restarts, (b) multiple services consume the same events, (c) throughput exceeds what a single process can handle.
- **Neo4j**: The in-memory graph is fast and simple. Neo4j adds network latency to every graph query. Only justified when: (a) graph exceeds single-process memory, (b) you need Cypher for ad-hoc investigation queries, (c) you need persistence across restarts.
- **Redis**: The in-memory signal cache is sufficient. Redis adds network round-trips. Only justified when: (a) multiple API instances need shared cache, (b) cache must survive restarts.

**Recommendation**: Mark all three as `OPTIONAL FUTURE SCALE UPGRADE`. Do not implement unless a specific scaling requirement demands it.

### OVER-ENGINEERING: "No Docker setup"

Not an architectural risk. Docker is a deployment concern. The application is a standard FastAPI app that can be containerized trivially. Not blocking for production readiness assessment.

---

## 3. Minimal Fix Plan (Priority Ordered)

### Tier 1: Critical Bugs (Must Fix — Incorrect Behavior)

| # | Bug | File | Lines | Impact |
|---|-----|------|-------|--------|
| 1 | Score scale mismatch | `rule_engine.py` | 67 | Final risk score unreliable |
| 2 | ML model signature crash | `fraud_ml_model.py` | 28-34 | ML engine crashes every call |
| 3 | ML prediction call mismatch | `fraud_ml_prediction.py` | 55 | Passes dict to positional params |
| 4 | Subscriber payload mismatch | `case_management_subscriber.py` | 48-51 | Cases never created |
| 5 | Subscriber payload mismatch | `feature_store_subscriber.py` | 52-66 | Features stored as zeros |
| 6 | Double temporal edges | `fraud_pipeline.py` | 88-89 | Velocity scores inflated 2x |

### Tier 2: High-ROI Performance (Should Fix)

| # | Issue | File | Lines | Impact |
|---|-------|------|-------|--------|
| 7 | O(E) temporal queries | `temporal_graph.py` | 76 | Pipeline latency scales with total edges |
| 8 | Event bus memory leak | `event_bus.py` | 94 | OOM under sustained load |

### Tier 3: Operational Safety (Fix When Possible)

| # | Issue | File | Impact |
|---|-------|------|--------|
| 9 | Wire temporal pruning | `temporal_graph.py` | Memory growth from timestamps |
| 10 | Per-engine error handling | `risk_orchestrator.py` | Single engine failure kills pipeline |

### NOT implementing now:

- Kafka migration — `OPTIONAL FUTURE SCALE UPGRADE`
- Neo4j migration — `OPTIONAL FUTURE SCALE UPGRADE`
- Redis signal cache — `OPTIONAL FUTURE SCALE UPGRADE`
- Async event handlers — premature optimization for current throughput
- Graph explosion caps — valid concern but requires fraud domain calibration
- Docker setup — deployment tooling, not an architectural fix

---

## 4. Detailed Patches

### Patch 1: Normalize RuleEngine score

**File**: `backend/app/risk_engines/rule_engine.py`
**Line**: 67

```python
# Before:
"score": float(score),

# After:
"score": min(float(score) / 100.0, 1.0),
```

**Rationale**: Max possible rule score is 55 (30 + 25). Dividing by 100 normalizes to `[0, 0.55]`. Using 100 as denominator leaves headroom for additional rules without re-calibration. `min(..., 1.0)` caps at 1.0 as a safety bound.

**Breaking changes**: The MLEngine reads `scores.get("rule_engine", 0)` and passes it to `predict_chargeback()` as `rule_score`. After normalization, rule_score changes from `0-55` to `0-0.55`. Since the ML model is broken anyway (BUG-2), this is safe — both fixes must land together.

---

### Patch 2: Fix ML model predict/train alignment

**File**: `backend/app/services/fraud_ml_model.py`
**Lines**: 10-34 (full rewrite of train + predict)

```python
from sklearn.linear_model import LogisticRegression
import numpy as np


class FraudMLModel:

    FEATURE_KEYS = [
        "amount",
        "rule_score",
        "device_risk_score",
        "reputation_score",
        "cluster_risk_score",
    ]

    def __init__(self):
        self.model = LogisticRegression()
        self._trained = False

    def train(self, dataset):
        X = []
        y = []

        for row in dataset:
            X.append([row.get(k, 0) for k in self.FEATURE_KEYS])
            y.append(row["label"])

        X = np.array(X)
        y = np.array(y)

        if len(X) > 0 and len(set(y)) > 1:
            self.model.fit(X, y)
            self._trained = True

    def predict(self, features: dict):
        if not self._trained:
            return 0.5

        X = np.array([[features.get(k, 0) for k in self.FEATURE_KEYS]])

        try:
            probability = self.model.predict_proba(X)[0][1]
            return round(float(probability), 3)
        except Exception:
            return 0.5
```

**Rationale**: Single `FEATURE_KEYS` list guarantees train/predict feature alignment. `_trained` flag prevents calling `predict_proba` on an unfitted model. Fallback to 0.5 ("uncertain") instead of crashing.

**Note**: `fraud_ml_prediction.py:55` already passes the correct dict — no change needed there once `predict()` accepts a dict.

---

### Patch 3: Fix case_management_subscriber payload navigation

**File**: `backend/app/subscribers/case_management_subscriber.py`
**Lines**: 48-51

```python
# Before:
transaction_id = fraud_result.get("transaction_id")
merchant_id = fraud_result.get("merchant_id")
ml_prediction = fraud_result.get("ml_prediction", {})
chargeback_probability = ml_prediction.get("chargeback_probability", 0.0)

# After:
transaction_id = fraud_result.get("transaction_id")
merchant_id = fraud_result.get("merchant_id")
inner = fraud_result.get("fraud_result", {})
ml_prediction = inner.get("signals", {}).get("ml_prediction", {})
chargeback_probability = ml_prediction.get("chargeback_probability", 0.0)
```

---

### Patch 4: Fix feature_store_subscriber payload navigation

**File**: `backend/app/subscribers/feature_store_subscriber.py`
**Lines**: 52-66

```python
# Before:
transaction_id = fraud_result.get("transaction_id")
merchant_id = fraud_result.get("merchant_id")
rule_score = fraud_result.get("rule_score", 0.0)
ml_prediction = fraud_result.get("ml_prediction", {})
# ...

# After:
transaction_id = fraud_result.get("transaction_id")
merchant_id = fraud_result.get("merchant_id")
inner = fraud_result.get("fraud_result", {})
scores = inner.get("scores", {})
signals = inner.get("signals", {})
rule_score = scores.get("rule_score", 0.0)
ml_prediction = signals.get("ml_prediction", {})
chargeback_probability = ml_prediction.get("chargeback_probability", 0.0)
features_used = ml_prediction.get("features_used", {})
amount = features_used.get("amount", 0.0)
device_risk_score = features_used.get("device_risk_score", 0.0)
reputation = signals.get("reputation", {})
reputation_score = reputation.get("reputation_score", 0.0)
graph_cluster = signals.get("graph_cluster", {})
cluster_risk_score = graph_cluster.get("cluster_risk_score", 0.0)
```

---

### Patch 5: Remove double temporal edges

**File**: `backend/app/services/fraud_pipeline.py`
**Lines**: 84-89

```python
# Before:
# --------------------------------------------------
# Temporal Graph Update
# --------------------------------------------------

temporal_graph.add_edge(tx_node, device_node)
temporal_graph.add_edge(tx_node, merchant_node)

# After:
# --------------------------------------------------
# Temporal Graph Update
# --------------------------------------------------
# NOTE: temporal edges are recorded automatically by fraud_graph.add_edge()
# in build_graph_from_transaction(). No explicit call needed here.
```

Remove lines 88-89 entirely. The comment block (84-87) can stay or go — cosmetic choice.

---

### Patch 6: Add temporal graph node index

**File**: `backend/app/services/temporal_graph.py`

In `__init__` (after line 41):
```python
self.node_index = defaultdict(set)  # node -> set of edge keys
```

In `add_edge` (after lines 58-59):
```python
self.node_index[node_a].add((node_a, node_b))
self.node_index[node_b].add((node_b, node_a))
```

Replace `recent_connections` (lines 65-83):
```python
def recent_connections(self, node: str, window_seconds: int = 120):
    now = datetime.utcnow().timestamp()
    neighbors = []
    with self._lock:
        for key in self.node_index.get(node, set()):
            timestamps = self.edges.get(key, [])
            if any(now - t <= window_seconds for t in timestamps):
                neighbors.append(key[1])
    return neighbors
```

In `prune_old_edges` (after `del self.edges[key]` at line 151, add):
```python
a, b = key
self.node_index[a].discard(key)
self.node_index[b].discard((b, a))
```

---

### Patch 7: Bound event bus idempotency set

**File**: `backend/app/services/event_bus.py`

In `__init__` (line 43):
```python
# Before:
self.processed_event_ids = set()

# After:
from collections import OrderedDict
self._max_idempotency_keys = 50000
self.processed_event_ids = OrderedDict()
```

In `publish` (lines 88-94):
```python
# Before:
if event_id in self.processed_event_ids:
    return {"status": "duplicate_event_skipped", "event_id": event_id}
self.processed_event_ids.add(event_id)

# After:
if event_id in self.processed_event_ids:
    return {"status": "duplicate_event_skipped", "event_id": event_id}
self.processed_event_ids[event_id] = True
if len(self.processed_event_ids) > self._max_idempotency_keys:
    self.processed_event_ids.popitem(last=False)
```

**Rationale**: `OrderedDict` gives O(1) lookup + O(1) insertion-order eviction. Caps memory at 50K event IDs (~4MB). Oldest IDs are evicted first, which is correct since duplicate events arrive within seconds, not days.

---

### Patch 8: Per-engine error handling in orchestrator

**File**: `backend/app/services/risk_orchestrator.py`
**Lines**: 131-134

```python
# Before:
for engine in self.engines:
    result = engine.evaluate(db, running_context)
    engines_output[engine.name] = result
    scores[engine.name] = result.get("score", 0.0)

# After:
import logging
logger = logging.getLogger("disputeguard.orchestrator")

for engine in self.engines:
    try:
        result = engine.evaluate(db, running_context)
        engines_output[engine.name] = result
        scores[engine.name] = result.get("score", 0.0)
    except Exception:
        logger.exception("Engine %s failed — using fallback score 0.5", engine.name)
        engines_output[engine.name] = {"score": 0.5, "details": {"error": "engine_failed"}}
        scores[engine.name] = 0.5
```

**Design choice**: Fallback score is 0.5 ("uncertain"), not 0.0 ("safe"). In fraud detection, a failed engine should NOT reduce the risk score. 0.5 is neutral and forces downstream review.

---

## 5. What Should NOT Be Implemented Yet

| Suggestion | Reason to defer |
|-----------|-----------------|
| Kafka event bus | Current throughput doesn't justify operational complexity. The in-memory bus works. |
| Neo4j graph database | In-memory graph is faster for current scale. Neo4j adds network latency per query. |
| Redis signal cache | Single-process cache is sufficient. Redis only needed with horizontal API scaling. |
| Async event handlers | Adds concurrency complexity. Fix only when latency SLA is measured and violated. |
| Graph explosion caps (DFS depth limit) | Valid concern but requires domain calibration — what's the right cap? Needs fraud team input. |
| Full test suite | Important but separate workstream. Should not block the critical bug fixes above. |
| PostgreSQL migration | Correct for production but a deployment concern, not a code fix. |
| IP intelligence engine | New feature, not a fix. Should go through product prioritization. |
| Entity resolution / fuzzy matching | Major new capability. Requires NLP/similarity infrastructure. |

---

## 6. Implementation Order

The patches have dependencies. Correct order:

1. **Patch 5** (remove double temporal edges) — standalone, no dependencies
2. **Patch 1** (normalize rule score) — standalone
3. **Patch 2** (fix ML model) — depends on Patch 1 being deployed simultaneously (rule_score scale changes)
4. **Patch 3** (fix case subscriber) — standalone
5. **Patch 4** (fix feature store subscriber) — standalone
6. **Patch 6** (temporal index) — standalone performance fix
7. **Patch 7** (bound event bus) — standalone memory fix
8. **Patch 8** (engine error handling) — standalone safety net

Patches 1+2 should be deployed together. All others are independent.
