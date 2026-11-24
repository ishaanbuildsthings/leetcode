# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerPathUndirected.py

# Euler path on an undirected graph: a walk that uses every edge exactly once. It may end where it started (a circuit
# counts as a path).
# edges: [(a, b), ...], labels 0..n-1 or 1..n (sized to the largest label, nothing to pass); repeated edges and
# self-loops are fine.
# start, end (optional): the nodes the path must start / end at. Left out, they're picked for you: with two odd-degree
# nodes the path runs between them (smaller label first); with none it's a circuit from any node with edges.
# Returns the nodes in walk order (len(edges) + 1 of them), or None if no such path exists (degrees don't allow one,
# edges not all reachable from the start, or a start / end that doesn't fit).
# No edges: [start] or [end] if one was given (None if both were given and differ), else [].
# eulerPathUndirected([(1, 2), (2, 3), (3, 1), (1, 4)]) -> [1, 3, 2, 1, 4]
# eulerPathUndirected([(1, 2), (2, 3)], start=3) -> [3, 2, 1]
# eulerPathUndirected([(1, 2), (1, 3), (1, 4)]) -> None
# O(N + M) time and space, N = largest label, M = number of edges
def eulerPathUndirected(edges, start=None, end=None):
    if not edges:
        if start is not None and end is not None and start != end:
            return None
        if start is not None:
            return [start]
        return [] if end is None else [end]
    size = max(max(a, b) for a, b in edges) + 1
    for node in (start, end):
        if node is not None:
            size = max(size, node + 1)
    adj = [[] for _ in range(size)]  # adj[node] = [(neighbor, edge id), ...], each edge sits in both endpoints' lists
    for edgeId, (a, b) in enumerate(edges):
        adj[a].append((b, edgeId))
        adj[b].append((a, edgeId))
    odd = [node for node in range(size) if len(adj[node]) % 2]
    if len(odd) not in (0, 2):
        return None
    if odd:
        for node in (start, end):
            if node is not None and node not in odd:
                return None
        if start is not None and end is not None and start == end:
            return None
        if start is None:
            start = odd[1] if end == odd[0] else odd[0]
    else:
        if start is not None and end is not None and start != end:
            return None
        if start is None:
            start = end if end is not None else edges[0][0]
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
