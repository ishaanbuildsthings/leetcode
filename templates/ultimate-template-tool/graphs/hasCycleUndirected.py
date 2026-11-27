# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/hasCycleUndirected.py

# hasCycle = hasCycleUndirected(edges)
#   edges is a list of undirected edges [[from, to], ...]
#   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
#   (a node with no edges can't be on a cycle, so how many nodes there are doesn't matter)
#   For example: hasCycleUndirected([[1, 2], [2, 3], [3, 1]])
#
# hasCycle -> True if there's a loop anywhere in the graph, e.g. True
#   A self-loop counts as a cycle, and so do two copies of the same edge, since you can go out
#   along one and come back along the other
#
#   hasCycleUndirected([[1, 2], [2, 3]]) -> False
#   hasCycleUndirected([[1, 2], [2, 1]]) -> True    (the same edge twice)
#
# O(V + E α(V)) time (union-find, so practically linear), O(V) space, V = largest label


def hasCycleUndirected(edges):
    size = 0
    for a, b in edges:
        if a < 0 or b < 0:
            raise ValueError(f"hasCycleUndirected: edge ({a}, {b}) has a negative label")
        size = max(size, a + 1, b + 1)
    parent = list(range(size))

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    # an edge between two nodes that are already connected closes a loop
    for a, b in edges:
        rootA, rootB = find(a), find(b)
        if rootA == rootB:
            return True
        parent[rootA] = rootB
    return False
