# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerCircuitDirected.py

# walk = eulerCircuitDirected(edges, start=None)
#   edges is a list of directed edges [[from, to], ...]; repeated edges and self-loops are fine
#   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
#   start is optional: the node the circuit has to start and end at. Left out, any node with edges
#   For example: eulerCircuitDirected([[1, 2], [2, 3], [3, 1]])
#
# walk -> the nodes in walking order, using every edge exactly once, e.g. [1, 2, 3, 1]
#   It has len(edges) + 1 nodes, and the first and last are the same node
#
#   None if there's no circuit: some node has more edges in than out (or out than in), some edge can't be reached
#   from the start, or the start you gave has no edges
#   With no edges at all: just the start if you gave one, else []
#
#   eulerCircuitDirected([[1, 2], [2, 3], [3, 1]], start=2) -> [2, 3, 1, 2]
#   eulerCircuitDirected([[1, 2], [2, 3]]) -> None
#
# O(V + E) time and space, V = largest label, E = number of edges
def eulerCircuitDirected(edges, start=None):
    if not edges:
        return [] if start is None else [start]
    size = max(max(a, b) for a, b in edges) + 1
    if start is not None:
        size = max(size, start + 1)
    adj = [[] for _ in range(size)]
    balance = [0] * size  # out-degree minus in-degree
    for a, b in edges:
        adj[a].append(b)
        balance[a] += 1
        balance[b] -= 1
    if any(balance):
        return None
    if start is None:
        start = edges[0][0]
    if not adj[start]:
        return None
    stack = [start]
    walk = []
    while stack:
        node = stack[-1]
        if adj[node]:
            stack.append(adj[node].pop())
        else:
            walk.append(stack.pop())
    if len(walk) != len(edges) + 1:
        return None
    walk.reverse()
    return walk
