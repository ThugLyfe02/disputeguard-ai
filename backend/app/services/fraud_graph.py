from collections import defaultdict


class FraudGraph:

    def __init__(self):
        self.graph = defaultdict(set)

    def add_relation(self, entity_a, entity_b):
        self.graph[entity_a].add(entity_b)
        self.graph[entity_b].add(entity_a)

    def get_connections(self, entity):
        return list(self.graph.get(entity, []))

    def detect_cluster(self, entity):

        visited = set()
        stack = [entity]

        while stack:
            node = stack.pop()

            if node not in visited:
                visited.add(node)
                stack.extend(self.graph[node] - visited)

        return list(visited)
