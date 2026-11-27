# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/bipartiteSplit.py

# split = bipartiteSplit(edges, numNodes, oneIndexed)
#   edges is a list of undirected edges [[node1, node2], ...]; repeated edges are fine
#   numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)
#   oneIndexed is True when the nodes are 1..numNodes, False when they're 0..numNodes-1
#   For example: bipartiteSplit([[1, 2], [2, 3], [3, 4]], 5, True)   (node 5 has no edges)
#
# split -> the two sides (side1, side2), each increasing, e.g. ([1, 3, 5], [2, 4])
#   Every edge goes between the two sides, none inside a side.
#   Each component's smallest node goes on side1. A node with no edges is on side1 too (it could go
#   on either side)
#
#   None if it's impossible: that happens exactly when there's a loop with an odd
#   number of edges, like a triangle. A self-loop always makes it impossible
#
#   bipartiteSplit([[1, 2], [2, 3], [3, 1]], 3, True) -> None
#
# O(V + E) time and space


def bipartiteSplit(edges, numNodes, oneIndexed: bool):
    firstNode = 1 if oneIndexed else 0
    size = firstNode + numNodes
    adj = [[] for _ in range(size)]
    for node1, node2 in edges:
        if not (firstNode <= node1 < size and firstNode <= node2 < size):
            raise ValueError(f"bipartiteSplit: edge ({node1}, {node2}) is outside the nodes {firstNode}..{size - 1}")
        adj[node1].append(node2)
        adj[node2].append(node1)

    # color each component starting from its smallest node (side 0); every edge has to join different sides
    side = [-1] * size
    for start in range(firstNode, size):
        if side[start] != -1:
            continue
        side[start] = 0
        stack = [start]
        while stack:
            node = stack.pop()
            for nxt in adj[node]:
                if side[nxt] == -1:
                    side[nxt] = 1 - side[node]
                    stack.append(nxt)
                elif side[nxt] == side[node]:
                    return None
    side1 = [node for node in range(firstNode, size) if side[node] == 0]
    side2 = [node for node in range(firstNode, size) if side[node] == 1]
    return side1, side2
