import sys

def treeMaxDistances(n, edges):
    """
    Returns list where res[i] = max distance from node i to any other node.
    Works with either 0-indexed nodes (in [0, n)) or 1-indexed nodes (in [1, n]).
    res has length n + 1; the unused slot is 0.
    """
    sz = n + 1
    adj = [[] for _ in range(sz)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    root = edges[0][0] if edges else 0
    parent = [-1] * sz
    visited = [False] * sz
    visited[root] = True
    order = []
    stack = [root]
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if visited[v]:
                continue
            visited[v] = True
            parent[v] = u
            stack.append(v)

    down2 = [[0, 0] for _ in range(sz)]
    argBest = [-1] * sz

    # dfs1: post-order
    for node in reversed(order):
        for adjN in adj[node]:
            if adjN == parent[node]:
                continue
            cand = down2[adjN][0] + 1
            if cand >= down2[node][0]:
                down2[node][1] = down2[node][0]
                down2[node][0] = cand
                argBest[node] = adjN
            elif cand > down2[node][1]:
                down2[node][1] = cand

    # dfs2: pre-order
    up = [0] * sz
    res = [0] * sz
    for node in order:
        res[node] = max(up[node], down2[node][0])
        for child in adj[node]:
            if child == parent[node]:
                continue
            bestDownExcl = down2[node][1] if argBest[node] == child else down2[node][0]
            up[child] = max(up[node] + 1, bestDownExcl + 1)

    return res