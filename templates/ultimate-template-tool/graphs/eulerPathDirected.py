# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerPathDirected.py

# walk = eulerPathDirected(edges, start=None, end=None)
#   edges is a list of directed edges [[from, to], ...]; repeated edges and self-loops are fine
#   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
#   start and end are optional: the nodes the walk has to start and end at. Left out, they're
#   picked for you: the node with one more edge out than in starts, and the node with one more in than out ends.
#   If every node has as many edges in as out, the walk is a circuit from any node with edges
#   For example: eulerPathDirected([[1, 2], [2, 3], [3, 1], [1, 4]])
#
# walk -> the nodes in walking order, using every edge exactly once, e.g. [1, 2, 3, 1, 4]
#   It has len(edges) + 1 nodes and may end where it started (a circuit counts)
#
#   None if there's no such walk: the degrees don't allow one, some edge can't be reached
#   from the start, or the start / end you gave doesn't fit
#   With no edges at all: just the start or end if you gave one, else []
#
#   eulerPathDirected([[1, 2], [2, 1]], start=2, end=2) -> [2, 1, 2]
#   eulerPathDirected([[1, 2], [1, 3]]) -> None
#
# O(V + E) time and space, V = largest label, E = number of edges
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
