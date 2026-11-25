# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/topoSort.py

# Topological sort of a directed graph (Kahn's algorithm), which doubles as the "is it a DAG?" check.
# edges: [(a, b), ...] meaning a -> b ("a must come before b", e.g. a is a prerequisite of b); repeated edges are fine,
# a self-loop is a cycle.
# n, oneIndexed (both required): the nodes are 0..n-1, or 1..n when oneIndexed is True. A node with no edges never
# shows up in the edge list but still has to appear in the order. Every edge must stay in that range.
# Returns None if the graph has a cycle (not a DAG). Otherwise every node exactly once, ordered so that for every edge
# a -> b, a comes BEFORE b: nodes with no incoming edges come first, the order you could take courses in. Reverse it
# for "everything a node points to comes first".
#   topoSort([(1, 3), (2, 3)], 3, oneIndexed=True)          -> [1, 2, 3]
#   topoSort([(0, 1)], 3, oneIndexed=False)                 -> [0, 2, 1]     (node 2 has no edges)
#   topoSort([(1, 2), (2, 3), (3, 1)], 3, oneIndexed=True)  -> None          (cycle)
#   isDag = topoSort(edges, n, oneIndexed) is not None
# O(V + E) time and space, V = n, E = number of edges


def topoSort(edges, n, oneIndexed: bool):
    if n < 0:
        raise ValueError(f"topoSort: needs n >= 0, got {n}")
    firstNode = 1 if oneIndexed else 0
    lastNode = firstNode + n - 1
    size = lastNode + 1
    adj = [[] for _ in range(size)]
    inDegree = [0] * size
    for a, b in edges:
        if not (firstNode <= a <= lastNode and firstNode <= b <= lastNode):
            raise ValueError(f"topoSort: edge ({a}, {b}) is outside the nodes {firstNode}..{lastNode}")
        adj[a].append(b)
        inDegree[b] += 1
    order = [node for node in range(firstNode, size) if not inDegree[node]]
    i = 0
    while i < len(order):
        node1 = order[i]
        i += 1
        for node2 in adj[node1]:
            inDegree[node2] -= 1
            if not inDegree[node2]:
                order.append(node2)
    return order if len(order) == n else None
