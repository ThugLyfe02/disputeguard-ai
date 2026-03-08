"""
fraud_network_graph.py

Fraud Intelligence Network Graph

Maintains a global, in-memory fraud intelligence graph connecting key
entities across the payment ecosystem:

    • Transactions  (tx_<id>)
    • Devices       (device_<hash>)
    • Merchants     (merchant_<id>)
    • Emails        (email_<address>)
    • Disputes      (dispute_<id>)

The graph is built incrementally as new transactions are processed and can be
queried to surface fraud signals such as:

    • Device reuse detection   – same device linked to many transactions or merchants
    • Cross-merchant fraud     – fraud-prone transactions spanning multiple merchants
    • Fraud ring detection     – clusters of tightly-connected entities acting in concert

Architecture mirrors network intelligence systems used by:
    Stripe Radar · Sift · Forter · Riskified

Usage
-----
    from app.services.fraud_network_graph import fraud_graph

    fraud_graph.build_graph_from_transaction(tx, device_hash, merchant_id)
    cluster = fraud_graph.detect_cluster(f"tx_{tx.id}")
    risk    = fraud_graph.calculate_network_risk(cluster)
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any


def _get_attr(obj: Any, key: str, default: Any = None) -> Any:
    """
    Read *key* from *obj* whether it is a plain dict or an ORM model instance.

    Parameters
    ----------
    obj:
        A dict or an object with attributes.
    key:
        The key / attribute name to look up.
    default:
        Value returned when the key is absent.
    """
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class FraudNetworkGraph:
    """
    In-memory fraud intelligence graph.

    Each node is a string with a typed prefix that identifies its category:
        ``tx_<id>``         – a payment transaction
        ``device_<hash>``   – a device fingerprint
        ``merchant_<id>``   – a merchant account
        ``email_<address>`` – a customer email address
        ``dispute_<id>``    – a chargeback / dispute record

    Edges are bidirectional and stored as adjacency sets so that lookups
    are O(1) and memory usage is proportional to the number of relationships.

    The graph is deliberately schema-free so that it can be expanded with new
    node types without code changes.

    Thread safety
    -------------
    All public mutation methods acquire :attr:`_lock` before modifying the
    graph so that the module-level :data:`fraud_graph` singleton is safe to
    use from multiple threads or async workers.

    Risk model constants
    --------------------
    The three constants below control the normalisation caps and weights used
    by :meth:`calculate_network_risk`.  They are surfaced as class attributes
    so that callers or subclasses can tune the model without touching the
    implementation.
    """

    # Maximum number of distinct merchants a single device may be linked to
    # before the device-reuse signal is treated as fully saturated (1.0).
    # Empirically, legitimate devices rarely appear at more than 2-3 merchants;
    # 5 is a conservative upper bound for normalisation.
    MAX_DEVICE_MERCHANT_LINKS: int = 5

    # Maximum number of distinct merchants in a cluster before the
    # cross-merchant-spread signal is treated as fully saturated (1.0).
    # Fraud rings typically span 5-15 merchants; 10 is the midpoint.
    MAX_CLUSTER_MERCHANTS: int = 10

    # Weights for the three risk signals – must sum to 1.0.
    # Dispute ratio is the strongest signal (0.5) because chargebacks directly
    # evidence fraud.  Device reuse (0.3) is a strong secondary signal.
    # Cross-merchant spread (0.2) amplifies the overall risk picture.
    DISPUTE_RATIO_WEIGHT: float = 0.5
    DEVICE_REUSE_WEIGHT: float = 0.3
    CROSS_MERCHANT_WEIGHT: float = 0.2

    def __init__(self) -> None:
        # adjacency representation: node -> {connected_nodes}
        self.graph: defaultdict[str, set[str]] = defaultdict(set)
        # Reentrant lock guards all writes to self.graph
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Core graph operations
    # ------------------------------------------------------------------

    def add_node(self, node: str) -> None:
        """
        Register a node in the graph without adding any edges.

        Ensures the node is present in the adjacency map even if it has no
        connections yet.  This is useful when an entity (e.g. a new device)
        should be visible in the graph before any relationships are known.

        Parameters
        ----------
        node:
            Prefixed node identifier, e.g. ``"device_abc123"``.
        """
        # Accessing the defaultdict key is sufficient to create the entry.
        with self._lock:
            _ = self.graph[node]

    def add_edge(self, node_a: str, node_b: str) -> None:
        """
        Create an undirected edge between two nodes.

        Both nodes are added to the graph if they do not already exist.
        The edge is stored in both adjacency sets so that traversal works in
        either direction.

        Parameters
        ----------
        node_a:
            Prefixed identifier for the first node, e.g. ``"tx_42"``.
        node_b:
            Prefixed identifier for the second node, e.g. ``"device_abc123"``.
        """
        with self._lock:
            self.graph[node_a].add(node_b)
            self.graph[node_b].add(node_a)

    def get_neighbors(self, node: str) -> list[str]:
        """
        Return all nodes directly connected to *node*.

        Parameters
        ----------
        node:
            Prefixed node identifier to look up.

        Returns
        -------
        list[str]
            List of neighbour node identifiers.  Returns an empty list when
            the node has no edges or does not exist in the graph.
        """
        return list(self.graph.get(node, set()))

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def build_graph_from_transaction(
        self,
        transaction: Any,
        device_hash: str,
        merchant_id: Any,
    ) -> None:
        """
        Expand the graph with entities derived from a single transaction.

        Edges added
        -----------
        - ``tx``       ↔ ``merchant``  (transaction belongs to a merchant)
        - ``tx``       ↔ ``device``    (transaction was initiated from a device)
        - ``tx``       ↔ ``email``     (transaction is associated with a customer email,
                                        if available on the transaction object/dict)
        - ``tx``       ↔ ``dispute``   (transaction is linked to a dispute,
                                        if available on the transaction object/dict)

        The function accepts both ORM model instances (attribute access) and
        plain dicts (key access) for *transaction*.

        Parameters
        ----------
        transaction:
            Transaction object or dict containing at least ``id`` and
            optionally ``email``, ``dispute_id`` / ``dispute`` fields.
        device_hash:
            Unique fingerprint string identifying the device used for the
            transaction, e.g. an MD5 of browser + IP attributes.
        merchant_id:
            Identifier of the merchant that processed the transaction.
        """

        tx_id = _get_attr(transaction, "id")
        if tx_id is None:
            return  # Cannot build a node without an identifier

        tx_node = f"tx_{tx_id}"
        device_node = f"device_{device_hash}"
        merchant_node = f"merchant_{merchant_id}"

        # Ensure the primary nodes exist even before edges are added
        self.add_node(tx_node)
        self.add_node(device_node)
        self.add_node(merchant_node)

        # Core structural edges
        self.add_edge(tx_node, device_node)
        self.add_edge(tx_node, merchant_node)

        # Optional: email association
        email = _get_attr(transaction, "email")
        if email:
            email_node = f"email_{email}"
            self.add_node(email_node)
            self.add_edge(tx_node, email_node)

        # Optional: dispute association (attribute may be an id or object)
        dispute_id = _get_attr(transaction, "dispute_id")
        if dispute_id is None:
            # Some models expose the dispute as a nested object
            dispute_obj = _get_attr(transaction, "dispute")
            if dispute_obj is not None:
                dispute_id = _get_attr(dispute_obj, "id")
        if dispute_id is not None:
            dispute_node = f"dispute_{dispute_id}"
            self.add_node(dispute_node)
            self.add_edge(tx_node, dispute_node)

    # ------------------------------------------------------------------
    # Cluster detection
    # ------------------------------------------------------------------

    def detect_cluster(self, start_node: str) -> list[str]:
        """
        Identify all nodes reachable from *start_node* (connected component).

        Uses an iterative depth-first search so that very large graphs do not
        cause Python recursion-limit errors.

        This is the primary primitive for fraud ring detection: all entities
        reachable from a known bad actor share the same connected component and
        are therefore candidates for coordinated fraud.

        Parameters
        ----------
        start_node:
            The node from which traversal begins, e.g. ``"tx_99"``.

        Returns
        -------
        list[str]
            All node identifiers in the same connected component as
            *start_node*, including *start_node* itself.  Returns an empty
            list when *start_node* is not present in the graph.
        """
        if start_node not in self.graph:
            return []

        visited: set[str] = set()
        stack: list[str] = [start_node]

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                # Only enqueue unvisited neighbours
                stack.extend(self.graph[node] - visited)

        return list(visited)

    # ------------------------------------------------------------------
    # Risk computation
    # ------------------------------------------------------------------

    def calculate_network_risk(self, cluster: list[str]) -> float:
        """
        Compute a normalised network risk score [0.0 – 1.0] for a cluster.

        The score is derived from three complementary signals:

        1. **Dispute ratio**
           The proportion of dispute nodes relative to transaction nodes in
           the cluster.  A high ratio signals an unusual number of chargebacks
           tied to a connected set of entities.

        2. **Device reuse**
           Counts how many merchant nodes are reachable from each device node
           in the cluster.  A device linked to many merchants is a strong
           indicator of carding or account-takeover campaigns.

        3. **Cross-merchant spread**
           The number of distinct merchants in the cluster.  Fraud rings
           typically spread their activity across merchants to stay below
           per-merchant alert thresholds.

        Each signal is independently normalised to [0.0, 1.0] and then
        combined with fixed weights that reflect empirical fraud patterns:

            score = DISPUTE_RATIO_WEIGHT  × dispute_ratio
                  + DEVICE_REUSE_WEIGHT   × device_reuse_signal
                  + CROSS_MERCHANT_WEIGHT × cross_merchant_signal

        See class-level constants for weight and cap values.

        Parameters
        ----------
        cluster:
            List of node identifiers as returned by :meth:`detect_cluster`.

        Returns
        -------
        float
            Risk score in the range [0.0, 1.0].  Returns ``0.0`` for empty or
            transaction-free clusters.
        """
        if not cluster:
            return 0.0

        dispute_nodes = [n for n in cluster if n.startswith("dispute_")]
        tx_nodes = [n for n in cluster if n.startswith("tx_")]
        device_nodes = [n for n in cluster if n.startswith("device_")]
        merchant_nodes = [n for n in cluster if n.startswith("merchant_")]

        # Signal 1: dispute ratio
        if tx_nodes:
            dispute_ratio = len(dispute_nodes) / len(tx_nodes)
        else:
            dispute_ratio = 0.0

        # Signal 2: device reuse – max merchants linked to a single device
        max_device_merchant_links = 0
        for device in device_nodes:
            merchant_links = sum(
                1 for nb in self.graph.get(device, set())
                if nb.startswith("merchant_")
            )
            if merchant_links > max_device_merchant_links:
                max_device_merchant_links = merchant_links

        device_reuse_signal = min(
            max_device_merchant_links / self.MAX_DEVICE_MERCHANT_LINKS, 1.0
        )

        # Signal 3: cross-merchant spread
        cross_merchant_signal = min(
            len(merchant_nodes) / self.MAX_CLUSTER_MERCHANTS, 1.0
        )

        score = (
            self.DISPUTE_RATIO_WEIGHT * dispute_ratio
            + self.DEVICE_REUSE_WEIGHT * device_reuse_signal
            + self.CROSS_MERCHANT_WEIGHT * cross_merchant_signal
        )

        return min(score, 1.0)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

#: Global fraud intelligence graph instance shared across the application.
#: Import this object to add nodes/edges or query the graph without
#: instantiating a new graph on every call.
fraud_graph = FraudNetworkGraph()


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

def add_node(node: str) -> None:
    """Add *node* to the global :data:`fraud_graph`. See :meth:`FraudNetworkGraph.add_node`."""
    fraud_graph.add_node(node)


def add_edge(node_a: str, node_b: str) -> None:
    """Add an edge to the global :data:`fraud_graph`. See :meth:`FraudNetworkGraph.add_edge`."""
    fraud_graph.add_edge(node_a, node_b)


def get_neighbors(node: str) -> list[str]:
    """Return neighbours from the global :data:`fraud_graph`. See :meth:`FraudNetworkGraph.get_neighbors`."""
    return fraud_graph.get_neighbors(node)


def build_graph_from_transaction(
    transaction: Any,
    device_hash: str,
    merchant_id: Any,
) -> None:
    """Expand the global :data:`fraud_graph` with a transaction. See :meth:`FraudNetworkGraph.build_graph_from_transaction`."""
    fraud_graph.build_graph_from_transaction(transaction, device_hash, merchant_id)


def detect_cluster(start_node: str) -> list[str]:
    """Detect a cluster in the global :data:`fraud_graph`. See :meth:`FraudNetworkGraph.detect_cluster`."""
    return fraud_graph.detect_cluster(start_node)


def calculate_network_risk(cluster: list[str]) -> float:
    """Compute risk for *cluster* using the global :data:`fraud_graph`. See :meth:`FraudNetworkGraph.calculate_network_risk`."""
    return fraud_graph.calculate_network_risk(cluster)
