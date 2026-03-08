"""
Fraud Intelligence Network Graph
=================================

Maintains a global, incrementally-built fraud intelligence graph that
connects key entities across the DisputeGuard AI platform:

    • Transactions  (tx_<id>)
    • Devices       (device_<hash>)
    • Emails        (email_<address>)
    • Merchants     (merchant_<id>)
    • Disputes      (dispute_<id>)

The graph supports:

    1. Incremental construction — nodes and edges can be added at any time.
    2. Neighbor queries      — retrieve all entities directly connected to a node.
    3. Cluster detection     — BFS traversal to find all reachable nodes from a
                               starting point.
    4. Network risk signals  — compute composite fraud-risk indicators from a
                               cluster of connected entities.

Fraud-intelligence features enabled by the graph:

    Device Reuse Detection
        Identifies when the same device fingerprint appears across multiple
        transactions or merchants — a common indicator of account-takeover
        and card-testing fraud.

    Cross-Merchant Fraud
        Tracks relationships across different merchants that share fraudulent
        transactions, enabling coordinated-attack detection.

    Fraud Ring Detection
        Analyses connected clusters to surface rings of colluding entities
        (e.g., mule networks, synthetic-identity groups).

Notes
-----
The in-memory store uses a ``defaultdict(set)`` for O(1) edge insertion and
O(degree) neighbour look-ups.  In production this would be backed by a
persistent graph database such as Neo4j, TigerGraph, or RedisGraph.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, List, Set


# ---------------------------------------------------------------------------
# Global in-memory graph
# ---------------------------------------------------------------------------

# { node_id: set(neighbour_ids) }
_graph: Dict[str, Set[str]] = defaultdict(set)


# ---------------------------------------------------------------------------
# Low-level graph primitives
# ---------------------------------------------------------------------------

def add_node(node: str) -> None:
    """Add *node* to the graph if it is not already present.

    Parameters
    ----------
    node:
        A prefixed node identifier, e.g. ``"tx_abc123"`` or
        ``"device_xyz789"``.
    """

    if node not in _graph:
        _graph[node]  # touching the defaultdict initialises the empty set


def add_edge(node_a: str, node_b: str) -> None:
    """Establish an undirected edge between *node_a* and *node_b*.

    Both nodes are created automatically if they do not already exist.

    Parameters
    ----------
    node_a:
        Source node identifier (prefixed).
    node_b:
        Target node identifier (prefixed).
    """

    # Avoid creating self-loops, which add noise for clustering/visualisation.
    if node_a == node_b:
        # Still honour the contract that nodes are created automatically.
        add_node(node_a)
        return
    _graph[node_a].add(node_b)
    _graph[node_b].add(node_a)


def get_neighbors(node: str) -> List[str]:
    """Return all nodes directly connected to *node*.

    Parameters
    ----------
    node:
        The node whose neighbours are requested.

    Returns
    -------
    list[str]
        Sorted list of neighbour node identifiers (empty list if *node* is
        unknown or has no edges).
    """

    return sorted(_graph.get(node, set()))


# ---------------------------------------------------------------------------
# Graph construction from transaction events
# ---------------------------------------------------------------------------

def build_graph_from_transaction(
    transaction: Dict[str, Any],
    device_hash: str,
    merchant_id: str,
) -> Dict[str, Any]:
    """Build or expand the fraud intelligence graph from a transaction event.

    Creates one node per entity class involved in the transaction and connects
    every pair of nodes with an undirected edge, producing a fully-connected
    sub-graph for that event.  Repeated calls with overlapping entities
    incrementally extend the global graph — shared nodes accumulate edges
    from every transaction that referenced them.

    Entity nodes created
    --------------------
    * ``tx_<transaction['id']>``           — the transaction itself
    * ``device_<device_hash>``             — the device fingerprint
    * ``merchant_<merchant_id>``           — the acquiring merchant
    * ``email_<transaction['email']>``     — the customer e-mail (when present)
    * ``dispute_<transaction['dispute_id']>`` — linked dispute (when present)

    Parameters
    ----------
    transaction:
        Mapping with at least an ``"id"`` key.  Optional keys recognised:
        ``"email"``, ``"dispute_id"``.
    device_hash:
        Opaque fingerprint that identifies the device used for the transaction.
    merchant_id:
        Identifier of the merchant that processed the transaction.

    Returns
    -------
    dict
        Summary of the update::

            {
                "transaction": "tx_abc123",
                "entities_linked": 4,
                "nodes": ["device_...", "merchant_...", "tx_...", ...]
            }
    """

    entities: List[str] = []

    tx_id = transaction.get("id")
    if not tx_id:
        raise ValueError("transaction must contain a non-empty 'id' field")

    tx_node = f"tx_{tx_id}"
    entities.append(tx_node)

    entities.append(f"device_{device_hash}")
    entities.append(f"merchant_{merchant_id}")

    email = transaction.get("email")
    if email:
        entities.append(f"email_{email}")

    dispute_id = transaction.get("dispute_id")
    if dispute_id:
        entities.append(f"dispute_{dispute_id}")

    # Ensure every entity has a node, then fully connect them.
    for entity in entities:
        add_node(entity)

    for i, entity in enumerate(entities):
        for other in entities[i + 1:]:
            add_edge(entity, other)

    return {
        "transaction": tx_node,
        "entities_linked": len(entities),
        "nodes": entities,
    }


# ---------------------------------------------------------------------------
# Cluster detection
# ---------------------------------------------------------------------------

def detect_cluster(start_node: str) -> List[str]:
    """Detect all nodes reachable from *start_node* via BFS traversal.

    Useful for identifying fraud rings — i.e. the full set of entities
    (devices, merchants, emails, transactions) that are transitively
    connected to a given seed entity.

    Parameters
    ----------
    start_node:
        The node from which the traversal begins.

    Returns
    -------
    list[str]
        Sorted list of all node identifiers in the same connected component
        as *start_node*.  Returns an empty list if *start_node* is not in
        the graph.
    """

    if start_node not in _graph:
        return []

    visited: Set[str] = set()
    queue: deque[str] = deque([start_node])

    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        for neighbour in _graph.get(node, set()):
            if neighbour not in visited:
                queue.append(neighbour)

    return sorted(visited)


# ---------------------------------------------------------------------------
# Risk computation
# ---------------------------------------------------------------------------

def calculate_network_risk(cluster: List[str]) -> Dict[str, Any]:
    """Compute fraud-risk signals from a cluster of connected entities.

    The composite risk score is derived from three independent sub-signals,
    each bounded to [0, 1]:

    device_reuse_score
        Elevated when many distinct device nodes share the same cluster,
        which suggests a single physical device being used for coordinated
        fraud across multiple identities.  Saturates at ≥ 5 devices.

    cross_merchant_score
        Elevated when the cluster spans multiple merchants, indicating
        coordinated or cross-merchant fraud activity.  Saturates at ≥ 5
        merchants.

    fraud_ring_score
        A holistic indicator that weighs all entity types.  Saturates when
        the cluster contains ≥ 10 mixed entities.

    The composite ``network_risk_score`` is the unweighted average of the
    three sub-signals, rounded to four decimal places.

    Parameters
    ----------
    cluster:
        List of node identifiers as returned by :func:`detect_cluster`.

    Returns
    -------
    dict
        Risk report::

            {
                "cluster_size":         int,
                "device_count":         int,
                "merchant_count":       int,
                "transaction_count":    int,
                "email_count":          int,
                "dispute_count":        int,
                "device_reuse_score":   float,   # [0, 1]
                "cross_merchant_score": float,   # [0, 1]
                "fraud_ring_score":     float,   # [0, 1]
                "network_risk_score":   float,   # [0, 1]  composite
            }
    """

    device_count = sum(1 for n in cluster if n.startswith("device_"))
    merchant_count = sum(1 for n in cluster if n.startswith("merchant_"))
    tx_count = sum(1 for n in cluster if n.startswith("tx_"))
    email_count = sum(1 for n in cluster if n.startswith("email_"))
    dispute_count = sum(1 for n in cluster if n.startswith("dispute_"))

    device_reuse_score = min(device_count / 5.0, 1.0)
    cross_merchant_score = min(merchant_count / 5.0, 1.0)
    fraud_ring_score = min(
        (device_count + merchant_count + tx_count) / 10.0, 1.0
    )

    network_risk_score = round(
        (device_reuse_score + cross_merchant_score + fraud_ring_score) / 3.0,
        4,
    )

    return {
        "cluster_size": len(cluster),
        "device_count": device_count,
        "merchant_count": merchant_count,
        "transaction_count": tx_count,
        "email_count": email_count,
        "dispute_count": dispute_count,
        "device_reuse_score": round(device_reuse_score, 4),
        "cross_merchant_score": round(cross_merchant_score, 4),
        "fraud_ring_score": round(fraud_ring_score, 4),
        "network_risk_score": network_risk_score,
    }
