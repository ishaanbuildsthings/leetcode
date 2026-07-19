# TEMPLATE BY ISHAANBUILDSTHINGS  (edges, NON-COMMUTATIVE path queries via a reverse hook)
# EXAMPLE  (max-subsegment sum along a path, over edge values)
# NodeData/EdgeData here is a tuple (total, best, pref, suf)
# def base(v):
#     e = max(0, v)
#     return (v, e, e, e)
# def mergeFn(L, R):              # L is the LEFT part (closer to A) on the path
#     lt, lb, lp, ls = L
#     rt, rb, rp, rs = R
#     return (lt + rt, max(lb, rb, ls + rp), max(lp, lt + rp), max(rs, rt + ls))
# def reverseFn(d):              # swap pref <-> suf
#     total, best, pref, suf = d
#     return (total, best, suf, pref)
# lifter = LiftEdgeReverse(0, edges, base, mergeFn, reverseFn)
# lifter.pathQuery(a, b)[1]   ->  max subsegment sum reading A -> B  (None if a == b)

# root = the root node (usually 0 or 1), exists since some utility functions are based on having a root
# edges = [[a, b, rawVal], [c, d, rawVal], ...] where rawVal is the raw data for the edge a<>b
# a and b (the node IDs) must be reasonably ranged, if they go up to 1e9 then we should compress outside
# base = (rawEdge) -> mapped val
# merge(leftData, rightData) -> data   (NON-commutative; left is closer to A on the path)
# reverse(data) -> data as if its underlying segment were traversed the other way
#   (max-subsegment: swap pref<->suf ; plain sum/min/max: return data unchanged)
class LiftEdgeReverse:
    # O(n log n) build time and space
    def __init__(self, root, edges, base, merge, reverse):
        self.n = root
        for u, v, w in edges:
            self.n = max(self.n, u, v)
        self.n += 1
        self.LOG = max(1, self.n.bit_length())
        self.base = base
        self.merge = merge
        self.reverse = reverse

        g = [[] for _ in range(self.n)]
        for u, v, w in edges:
            g[u].append((v, w))
            g[v].append((u, w))

        self.depths = [0] * self.n
        self.up = [[0] * self.n for _ in range(self.LOG)]
        self.upData = [[None] * self.n for _ in range(self.LOG)]

        stack = [(root, root, None, False)]
        while stack:
            node, parent, valAbove, visited = stack.pop()
            if visited:
                continue
            self.depths[node] = 0 if node == root else self.depths[parent] + 1
            self.up[0][node] = parent
            if node != root:
                self.upData[0][node] = base(valAbove)   # edge ABOVE node (directional keying)
            for k in range(1, self.LOG):
                mid = self.up[k - 1][node]
                self.up[k][node] = self.up[k - 1][mid]
                # shallower half (mid) is LEFT of deeper half (node): top-down order
                a = self.upData[k - 1][mid]
                b = self.upData[k - 1][node]
                if a is None:
                    self.upData[k][node] = b
                elif b is None:
                    self.upData[k][node] = a
                else:
                    self.upData[k][node] = merge(a, b)
            stack.append((node, parent, valAbove, True))
            for child, childVal in g[node]:
                if child != parent:
                    stack.append((child, node, childVal, False))

    # kth steps above `node`
    # always returns root if k steps shoots past the root
    # O(log N)
    def kthAncestor(self, node, kth):
        for k in range(self.LOG):
            if (kth >> k) & 1:
                node = self.up[k][node]
        return node

    # O(log N)
    def lca(self, a, b):
        if self.depths[a] < self.depths[b]:
            a, b = b, a
        diff = self.depths[a] - self.depths[b]
        for k in range(self.LOG):
            if (diff >> k) & 1:
                a = self.up[k][a]
        if a == b:
            return a
        for k in range(self.LOG - 1, -1, -1):
            if self.up[k][a] != self.up[k][b]:
                a = self.up[k][a]
                b = self.up[k][b]
        return self.up[0][a]

    # unweighted path distance from A<>B
    # O(log N)
    def pathDist(self, a, b):
        ab = self.lca(a, b)
        return self.depths[a] + self.depths[b] - 2 * self.depths[ab]

    # the median node, which is the only node on all three paths: A<>B, B<>C, A<>C
    # O(log N)
    def median(self, a, b, c):
        return self.lca(a, b) ^ self.lca(a, c) ^ self.lca(b, c)

    # k-th node on the A->B path, 1-indexed
    # -1 if OOB
    # O(log N)
    def kthOnPath(self, a, b, kth):
        ab = self.lca(a, b)
        distA = self.depths[a] - self.depths[ab]
        distB = self.depths[b] - self.depths[ab]
        totalLen = distA + distB + 1
        if kth < 1 or kth > totalLen:
            return -1
        if kth <= distA + 1:
            return self.kthAncestor(a, kth - 1)
        return self.kthAncestor(b, distB - (kth - distA - 1))

    # how many edges to cross to get from `node` onto any node on the A<>B path
    # O(log N)
    def distToPath(self, a, b, node):
        return self.pathDist(self.median(a, b, node), node)

    # returns a bool if `node` is on the path A<>B
    # O(log N)
    def inPath(self, a, b, node):
        return self.median(a, b, node) == node

    # lca of a and b if the tree were rooted at r instead of the build root
    # O(log N)
    def lcaUnderR(self, r, a, b):
        return self.median(a, b, r)

    # intersection of path a<>b and path x<>y (endpoint order doesn't matter).
    # returns (p, q), the endpoints of the shared subpath (p == q if a single node),
    # or None if the two paths are disjoint.
    # O(log N)
    def pathIntersection(self, a, b, x, y):
        cands = [
            self.median(a, b, x), self.median(a, b, y),
            self.median(x, y, a), self.median(x, y, b),
        ]
        onBoth = [c for c in cands
                  if self.inPath(a, b, c) and self.inPath(x, y, c)]
        if not onBoth:
            return None
        p = q = onBoth[0]
        best = -1
        for i in range(len(onBoth)):
            for j in range(i, len(onBoth)):
                d = self.pathDist(onBoth[i], onBoth[j])
                if d > best:
                    best = d
                    p, q = onBoth[i], onBoth[j]
        return (p, q)

    # aggregated edge data for the k edges going up from `node` (edge above node first),
    # in TOP-DOWN path order (shallow -> deep). None if k == 0.
    # O(log N)
    def liftQuery(self, node, k):
        acc = None
        rem = k
        for b in range(self.LOG - 1, -1, -1):
            if rem >= (1 << b):
                d = self.upData[b][node]
                if d is not None:
                    acc = d if acc is None else self.merge(d, acc)   # new block shallower -> LEFT
                node = self.up[b][node]
                rem -= (1 << b)
        return acc

    # aggregated edge data over the path A -> B, read in that direction (NON-commutative).
    # the edge above the LCA is NOT on the path. None if A == B.
    # O(log N)
    def pathQuery(self, a, b):
        l = self.lca(a, b)
        da = self.depths[a] - self.depths[l]
        db = self.depths[b] - self.depths[l]
        left = self.liftQuery(a, da) if da > 0 else None    # a-arm edges, top-down
        right = self.liftQuery(b, db) if db > 0 else None   # b-arm edges, top-down
        res = None
        if left is not None:
            res = self.reverse(left)                        # reverse a-arm: reads a -> L
        if right is not None:
            res = right if res is None else self.merge(res, right)   # then L -> b
        return res