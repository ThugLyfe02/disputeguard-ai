from collections import defaultdict


class FraudKnowledgeGraph:

    def __init__(self):

        self.nodes = {}
        self.edges = defaultdict(set)

    def add_node(self, node_id, node_type):

        self.nodes[node_id] = node_type

    def add_edge(self, node_a, node_b):

        self.edges[node_a].add(node_b)
        self.edges[node_b].add(node_a)

    def get_neighbors(self, node):

        return list(self.edges[node])

    def detect_community(self, start_node):

        visited = set()
        stack = [start_node]

        while stack:

            node = stack.pop()

            if node not in visited:

                visited.add(node)

                stack.extend(self.edges[node] - visited)

        return visited