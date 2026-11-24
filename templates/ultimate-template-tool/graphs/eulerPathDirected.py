# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerPathDirected.py

# Euler path on a directed graph: a walk that uses every edge exactly once. It may end where it started (a circuit
# counts as a path).
# edges: [(a, b), ...] meaning a -> b, labels 0..n-1 or 1..n (sized to the largest label, nothing to pass); repeated
# edges and self-loops are fine.
# start, end (optional): the nodes the path must start / end at. Left out, they're picked for you: the node with one
# more out than in starts and the node with one more in than out ends; if every node is balanced the path is a circuit
# from any node with edges.
# Returns the nodes in walk order (len(edges) + 1 of them), or None if no such path exists (degrees don't allow one,
# edges not all reachable from the start, or a start / end that doesn't fit).
# No edges: [start] or [end] if one was given (None if both were given and differ), else [].
# eulerPathDirected([(1, 2), (2, 3), (3, 1), (1, 4)]) -> [1, 2, 3, 1, 4]
# eulerPathDirected([(1, 2), (2, 1)], start=2, end=2) -> [2, 1, 2]
# eulerPathDirected([(1, 2), (1, 3)]) -> None
# O(N + M) time and space, N = largest label, M = number of edges
def eulerPathDirected(edges, start=None, end=None):
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
    adj = [[] for _ in range(size)]
    balance = [0] * size  # out-degree minus in-degree
    for a, b in edges:
        adj[a].append(b)
        balance[a] += 1
        balance[b] -= 1
    extraOut = [node for node in range(size) if balance[node] == 1]
    extraIn = [node for node in range(size) if balance[node] == -1]
    if len(extraOut) + len(extraIn) != sum(1 for x in balance if x):
        return None  # some node is off by 2 or more
    if len(extraOut) > 1 or len(extraOut) != len(extraIn):
        return None
    if extraOut:
        if start is not None and start != extraOut[0]:
            return None
        if end is not None and end != extraIn[0]:
            return None
        start = extraOut[0]
    else:
        if start is not None and end is not None and start != end:
            return None
        if start is None:
            start = end if end is not None else edges[0][0]
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
