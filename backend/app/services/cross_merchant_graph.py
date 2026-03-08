from collections import defaultdict

from app.models.transaction import Transaction
from app.models.dispute import Dispute


class CrossMerchantGraph:

    def __init__(self):
        self.graph = defaultdict(set)

    def add_relation(self, a, b):
        self.graph[a].add(b)
        self.graph[b].add(a)

    def detect_cluster(self, entity):

        visited = set()
        stack = [entity]

        while stack:
            node = stack.pop()

            if node not in visited:
                visited.add(node)
                stack.extend(self.graph[node] - visited)

        return list(visited)


def build_cross_merchant_graph(db):

    graph = CrossMerchantGraph()

    transactions = db.query(Transaction).all()

    for tx in transactions:

        merchant = f"merchant_{tx.merchant_id}"
        customer = f"cust_{tx.customer_id}"

        graph.add_relation(merchant, customer)

        if hasattr(tx, "device_hash") and tx.device_hash:
            graph.add_relation(customer, f"device_{tx.device_hash}")

        graph.add_relation(customer, f"tx_{tx.id}")

    disputes = db.query(Dispute).all()

    for dispute in disputes:
        graph.add_relation(f"tx_{dispute.transaction_id}", f"dispute_{dispute.id}")

    return graph
