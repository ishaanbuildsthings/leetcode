# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/reroot/FarthestNode.py

# For every node, the farthest OTHER node (by edge count) and its distance
# edges = [[a, b], [c, d], ...]: an unrooted tree with at least 2 nodes
# labels can be 0..n-1 or 1..n, no flag needed: the output is sized to the largest label
#   0-indexed -> length n
#   1-indexed -> length n + 1, index 0 is an unused dummy holding (-1, -1)
# res = farthestNodes([[0, 1], [1, 2], [1, 3]])
#   res = [(2, 2), (1, 0), (2, 0), (2, 0)]   res[i] = (distance, farthest node)
# ties go to the smallest node id
# O(n) time and space, iterative (no recursion limit issues)
def farthestNodes(edges):
    size = max(max(a, b) for a, b in edges) + 1
    adj = [[] for _ in range(size)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    root = edges[0][0]
    parent = [-1] * size
    order = [root]
    for cur in order:
        par = parent[cur]
        for nxt in adj[cur]:
            if nxt != par:
                parent[nxt] = cur
                order.append(nxt)

    # best and second best (dist, node) strictly inside each subtree, through different children
    best1D = [-1] * size
    best1N = [-1] * size
    best1C = [-1] * size
    best2D = [-1] * size
    best2N = [-1] * size
    for i in range(len(order) - 1, 0, -1):
        cur = order[i]
        par = parent[cur]
        if best1N[cur] != -1:
            d = best1D[cur] + 1
            nd = best1N[cur]
        else:
            d = 1
            nd = cur
        if best1N[par] == -1 or d > best1D[par] or (d == best1D[par] and nd < best1N[par]):
            best2D[par] = best1D[par]
            best2N[par] = best1N[par]
            best1D[par] = d
            best1N[par] = nd
            best1C[par] = cur
        elif best2N[par] == -1 or d > best2D[par] or (d == best2D[par] and nd < best2N[par]):
            best2D[par] = d
            best2N[par] = nd

    # best (dist, node) reached by first stepping to the parent
    upD = [-1] * size
    upN = [-1] * size
    for i in range(1, len(order)):
        cur = order[i]
        par = parent[cur]
        d = 1
        nd = par
        if upN[par] != -1:
            cd = upD[par] + 1
            cn = upN[par]
            if cd > d or (cd == d and cn < nd):
                d = cd
                nd = cn
        if best1C[par] == cur:
            sd = best2D[par]
            sn = best2N[par]
        else:
            sd = best1D[par]
            sn = best1N[par]
        if sn != -1:
            cd = sd + 1
            if cd > d or (cd == d and sn < nd):
                d = cd
                nd = sn
        upD[cur] = d
        upN[cur] = nd

    res = [(-1, -1)] * size
    for cur in order:
        d = upD[cur]
        nd = upN[cur]
        if best1N[cur] != -1 and (nd == -1 or best1D[cur] > d or (best1D[cur] == d and best1N[cur] < nd)):
            d = best1D[cur]
            nd = best1N[cur]
        res[cur] = (d, nd)
    return res
