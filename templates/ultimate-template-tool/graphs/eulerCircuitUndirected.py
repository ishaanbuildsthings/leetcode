# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerCircuitUndirected.py

# Euler circuit on an undirected graph: a walk that uses every edge exactly once and ends where it started.
# edges: [(a, b), ...], labels 0..n-1 or 1..n (sized to the largest label, nothing to pass); repeated edges and
# self-loops are fine.
# start (optional): the node the circuit must start and end at; any node with edges if left out.
# Returns the nodes in walk order (len(edges) + 1 of them, first == last), or None if no circuit exists (some node
# has odd degree, edges not all reachable from the start, or a start that has no edges).
# No edges: [start] if a start was given, else [].
# eulerCircuitUndirected([(1, 2), (2, 3), (3, 1)]) -> [1, 3, 2, 1]
# eulerCircuitUndirected([(1, 2), (2, 3), (3, 1)], start=2) -> [2, 3, 1, 2]
# eulerCircuitUndirected([(1, 2), (2, 3)]) -> None
# O(V + E) time and space, V = largest label, E = number of edges
def eulerCircuitUndirected(edges, start=None):
    if not edges:
        return [] if start is None else [start]
    size = max(max(a, b) for a, b in edges) + 1
    if start is not None:
        size = max(size, start + 1)
    adj = [[] for _ in range(size)]  # adj[node] = [(neighbor, edge id), ...], each edge sits in both endpoints' lists
    for edgeId, (a, b) in enumerate(edges):
        adj[a].append((b, edgeId))
        adj[b].append((a, edgeId))
    if any(len(adj[node]) % 2 for node in range(size)):
        return None
    if start is None:
        start = edges[0][0]
    if not adj[start]:
        return None
    used = [False] * len(edges)
    stack = [start]
    walk = []
    while stack:
        node = stack[-1]
        while adj[node] and used[adj[node][-1][1]]:
            adj[node].pop()  # (the other copy of an edge already walked from its other end)
        if adj[node]:
            nxt, edgeId = adj[node].pop()
            used[edgeId] = True
            stack.append(nxt)
        else:
            walk.append(stack.pop())
    if len(walk) != len(edges) + 1:
        return None
    walk.reverse()
    return walk
