# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/topoSort.py

# order = topoSort(edges, numNodes, oneIndexed)
#   edges is a list of directed edges [[from, to], ...], meaning from has to come before to
#   numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)
#   oneIndexed is True when the nodes are 1..numNodes, False when they're 0..numNodes-1
#   For example: topoSort([[1, 3], [2, 3], [3, 4]], 4, True)
#
# order -> every node exactly once, with from before to for every edge, e.g. [1, 2, 3, 4]
#   Nodes with nothing pointing to them come first, like an order you could take courses in.
#   Reverse it if you want everything a node points to to come first
#
#   None if the graph has a cycle, since then no order works. So this is also the
#   "is it a DAG?" check: isDag = topoSort(edges, numNodes, oneIndexed) is not None
#
# O(V + E) time and space


def topoSort(edges, numNodes, oneIndexed: bool):
    if numNodes < 0:
        raise ValueError(f"topoSort: needs numNodes >= 0, got {numNodes}")
    firstNode = 1 if oneIndexed else 0
    lastNode = firstNode + numNodes - 1
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
    return order if len(order) == numNodes else None
