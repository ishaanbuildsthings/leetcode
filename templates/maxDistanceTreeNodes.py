# ⚠️ Not optimized
# ✅ Passed on https://codeforces.com/contest/1822/submission/360265821
# O(n) time to get the maximum distance + max distance node, for all nodes
# Uses iterative DFS to avoid recursion limits

def farthestInfoPerNode(edges):
    """
    Input: edges of a tree (list of (u, v), length = n-1).
      - Node labels may be 0..n-1 or 1..n (auto-detected).
      - We infer:
          oneBased = (min label == 1)
          n       = max label            if oneBased
                    max label + 1        if 0-based
      - Returns arrays sized to maxLabel + 1:
          if 1-based: size n+1, index 0 exists but is unused
          if 0-based: size n,   indices 0..n-1 used

    Output:
      maxDist[u] = eccentricity of u (maximum distance in edges from u to any node)
      farNode[u] = a node achieving maxDist[u]

    Time: O(n)
    Space: O(n)
    """
    if not edges:
        return [], []

    mn = 10**18
    mx = -10**18
    for a, b in edges:
        if a < mn: mn = a
        if b < mn: mn = b
        if a > mx: mx = a
        if b > mx: mx = b

    oneBased = (mn == 1)
    n = mx if oneBased else (mx + 1)
    base = 1 if oneBased else 0
    root = base
    N = n + 1 if oneBased else n

    adj = [[] for _ in range(N)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    # parent[root] = root as a visited marker during DFS, then set to -1 after.
    parent = [-1] * N
    order = []

    # Iterative DFS gives a traversal order; reversing it yields postorder.
    stack = [root]
    parent[root] = root
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if v == parent[u]:
                continue
            if parent[v] != -1:
                continue
            parent[v] = u
            stack.append(v)
    parent[root] = -1

    # downBest[u] = best distance from u down into its rooted subtree
    # downNode[u] = endpoint node achieving downBest[u]
    downBest = [0] * N
    downNode = [-1] * N

    # top1/top2 store best and 2nd-best downward candidates from u among its children:
    # top1Dist[u], top1Node[u] = best (distance, endpoint)
    # top2Dist[u], top2Node[u] = second-best
    top1Dist = [0] * N
    top1Node = [-1] * N
    top2Dist = [0] * N
    top2Node = [-1] * N

    # Postorder DP: compute downBest/downNode and top1/top2
    for u in reversed(order):
        best1d, best1n = 0, u
        best2d, best2n = 0, u

        for v in adj[u]:
            if v == parent[u]:
                continue
            candDist = 1 + downBest[v]
            candNode = downNode[v]
            if candDist > best1d:
                best2d, best2n = best1d, best1n
                best1d, best1n = candDist, candNode
            elif candDist > best2d:
                best2d, best2n = candDist, candNode

        top1Dist[u], top1Node[u] = best1d, best1n
        top2Dist[u], top2Node[u] = best2d, best2n
        downBest[u], downNode[u] = best1d, best1n

    # upBest[u] = best distance from u to a node NOT in its subtree via parent side
    # upNode[u] = endpoint node achieving upBest[u]
    upBest = [0] * N
    upNode = [-1] * N
    upBest[root] = 0
    upNode[root] = root

    # Preorder DP: push "up" information to children
    for u in order:
        for v in adj[u]:
            if v == parent[u]:
                continue

            # best path starting at u that does NOT go into v's subtree:
            bestExclDist = top1Dist[u]
            bestExclNode = top1Node[u]
            if bestExclDist == 1 + downBest[v] and bestExclNode == downNode[v]:
                bestExclDist = top2Dist[u]
                bestExclNode = top2Node[u]

            # child v can reach those endpoints by paying 1 edge to go v->u
            cand1Dist = 1 + bestExclDist
            cand1Node = bestExclNode

            cand2Dist = 1 + upBest[u]
            cand2Node = upNode[u]

            if cand1Dist >= cand2Dist:
                upBest[v] = cand1Dist
                upNode[v] = cand1Node
            else:
                upBest[v] = cand2Dist
                upNode[v] = cand2Node

    # Final eccentricity per node = max(down, up)
    maxDist = [0] * N
    farNode = [-1] * N
    for u in range(base, base + n):
        if downBest[u] >= upBest[u]:
            maxDist[u] = downBest[u]
            farNode[u] = downNode[u]
        else:
            maxDist[u] = upBest[u]
            farNode[u] = upNode[u]

    return maxDist, farNode
