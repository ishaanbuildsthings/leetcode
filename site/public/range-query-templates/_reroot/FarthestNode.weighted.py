# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/reroot/FarthestNode.weighted.py

# For every node, the farthest OTHER node (by total edge weight) and its distance
# edges = [[a, b, w], [c, d, w], ...]: an unrooted tree with at least 2 nodes, any int weights (negative and 0 ok)
# labels can be 0..n-1 or 1..n, no flag needed: the output is sized to the largest label
#   0-indexed -> length n
#   1-indexed -> length n + 1, index 0 is an unused dummy holding (-1, -1)
# res = farthestNodes([[0, 1, 5], [1, 2, 3], [1, 3, 4]])
#   res = [(9, 3), (5, 0), (8, 0), (9, 0)]   res[i] = (distance, farthest node)
# ties go to the smallest node id
# O(n) time and space, iterative (no recursion limit issues)
def farthestNodes(edges):
    size = max(max(a, b) for a, b, _ in edges) + 1
    adj = [[] for _ in range(size)]
    for a, b, w in edges:
        adj[a].append((b, w))
        adj[b].append((a, w))

    root = edges[0][0]
    parent = [-1] * size
    parentW = [0] * size
    order = [root]
    for cur in order:
        par = parent[cur]
        for nxt, w in adj[cur]:
            if nxt != par:
                parent[nxt] = cur
                parentW[nxt] = w
                order.append(nxt)

    # best and second best (dist, node) strictly inside each subtree, through different children
    best1D = [0] * size
    best1N = [-1] * size
    best1C = [-1] * size
    best2D = [0] * size
    best2N = [-1] * size
    for i in range(len(order) - 1, 0, -1):
        cur = order[i]
        par = parent[cur]
        # stop at cur itself, or keep going down into its subtree
        d = 0
        nd = cur
        if best1N[cur] != -1 and (best1D[cur] > 0 or (best1D[cur] == 0 and best1N[cur] < cur)):
            d = best1D[cur]
            nd = best1N[cur]
        d += parentW[cur]
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
    upD = [0] * size
    upN = [-1] * size
    for i in range(1, len(order)):
        cur = order[i]
        par = parent[cur]
        w = parentW[cur]
        d = w
        nd = par
        if upN[par] != -1:
            cd = upD[par] + w
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
            cd = sd + w
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
