# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerCircuitDirected.py

# Euler circuit on a directed graph: a walk that uses every edge exactly once and ends where it started.
# edges: [(a, b), ...] meaning a -> b, labels 0..n-1 or 1..n (sized to the largest label, nothing to pass); repeated
# edges and self-loops are fine.
# start (optional): the node the circuit must start and end at; any node with edges if left out.
# Returns the nodes in walk order (len(edges) + 1 of them, first == last), or None if no circuit exists (some node's
# in-degree != out-degree, edges not all reachable from the start, or a start that has no edges).
# No edges: [start] if a start was given, else [].
# eulerCircuitDirected([(1, 2), (2, 3), (3, 1)]) -> [1, 2, 3, 1]
# eulerCircuitDirected([(1, 2), (2, 3), (3, 1)], start=2) -> [2, 3, 1, 2]
# eulerCircuitDirected([(1, 2), (2, 3)]) -> None
# O(N + M) time and space, N = largest label, M = number of edges
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
