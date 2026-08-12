# O(n log n)
# pass in a list of edges [(a, b), (c, d), ...]
# get out a list of [(subtreeRoot, { node1 : node1Children, node2 : node2Children, ...}), ...]
# with edges == [] it returns [(0, {0: []})]
def centroidDecomp(edges):
    arrSize = 1
    for u, v in edges:
        if u >= arrSize: arrSize = u + 1
        if v >= arrSize: arrSize = v + 1
    adj = [[] for _ in range(arrSize)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    removed = [False] * arrSize
    sz = [0] * arrSize
    par = [-1] * arrSize
    res = []
    stack = [edges[0][0] if edges else 0]
    while stack:
        start = stack.pop()
        order = []
        dfs = [start]
        par[start] = -1
        while dfs:
            node = dfs.pop()
            order.append(node)
            for nxt in adj[node]:
                if nxt != par[node] and not removed[nxt]:
                    par[nxt] = node
                    dfs.append(nxt)
        total = len(order)
        for node in order:
            sz[node] = 1
        for node in reversed(order):
            if par[node] != -1:
                sz[par[node]] += sz[node]
        centroid = start
        while True:
            heavy = -1
            for nxt in adj[centroid]:
                if nxt != par[centroid] and not removed[nxt] and sz[nxt] * 2 > total:
                    heavy = nxt
                    break
            if heavy == -1:
                break
            centroid = heavy
        children = {centroid: []}
        bfs = [centroid]
        while bfs:
            node = bfs.pop()
            kids = children[node]
            for nxt in adj[node]:
                if not removed[nxt] and nxt not in children:
                    children[nxt] = []
                    kids.append(nxt)
                    bfs.append(nxt)
        res.append((centroid, children))
        removed[centroid] = True
        for nxt in adj[centroid]:
            if not removed[nxt]:
                stack.append(nxt)
    return res