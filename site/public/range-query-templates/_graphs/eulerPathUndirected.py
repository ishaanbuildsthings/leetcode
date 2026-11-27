# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerPathUndirected.py

# walk = eulerPathUndirected(edges, start=None, end=None)
#   edges is a list of undirected edges [[node1, node2], ...]; repeated edges and self-loops are fine
#   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
#   start and end are optional: the nodes the walk has to start and end at. Left out, they're
#   picked for you: with two odd-degree nodes, the path runs from one to the other.
#   If every node has even degree, the walk is a circuit from any node with edges
#   For example: eulerPathUndirected([[1, 2], [2, 3], [3, 1], [1, 4]])
#
# walk -> the nodes in walking order, using every edge exactly once, e.g. [1, 3, 2, 1, 4]
#   It has len(edges) + 1 nodes and may end where it started (a circuit counts)
#
#   None if there's no such walk: the degrees don't allow one, some edge can't be reached
#   from the start, or the start / end you gave doesn't fit
#   With no edges at all: just the start or end if you gave one, else []
#
#   eulerPathUndirected([[1, 2], [2, 3]], start=3) -> [3, 2, 1]
#   eulerPathUndirected([[1, 2], [1, 3], [1, 4]]) -> None
#
# O(V + E) time and space, V = largest label, E = number of edges
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
