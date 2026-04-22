# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# Returns list where res[i] = sum of distances from node i to all other nodes.
# numNodes is the number of nodes in the tree.
# Node labels must be either 0-indexed in [0, numNodes) or 1-indexed in [1, numNodes].
# res has length numNodes + 1; the unused slot (res[0] or res[numNodes]) is 0.
# Iterative — safe for deep trees.
def treeSumOfDistances(numNodes, edges):
    sz = numNodes + 1
    adj = [[] for _ in range(sz)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    parent = [-1] * sz
    order = []

    root = edges[0][0] if edges else 0

    visited = [False] * sz
    visited[root] = True
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

    # dfs1: post-order — subtree sizes and down[u] = sum of dist from u into its subtree
    sub = [1] * sz
    down = [0] * sz
    for i in range(len(order) - 1, -1, -1):
        node = order[i]
        for child in adj[node]:
            if child == parent[node]:
                continue
            sub[node] += sub[child]
            down[node] += down[child] + sub[child]

    # dfs2: pre-order — reroot
    full = [0] * sz
    full[root] = down[root]
    for node in order:
        for child in adj[node]:
            if child == parent[node]:
                continue
            full[child] = full[node] - sub[child] + (numNodes - sub[child])

    return full