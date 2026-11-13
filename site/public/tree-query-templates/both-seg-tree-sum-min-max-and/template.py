# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-seg-tree-sum-min-max-and/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/seg-tree-sum-min-max-and/template.py
# @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgeNearestAncestorGtX edgeNearestAncestorGteX edgeNearestAncestorLtX edgeNearestAncestorLteX edgePathAND edgePathFirstGtX edgePathFirstGteX edgePathFirstLtX edgePathFirstLteX edgePathLastGtX edgePathLastGteX edgePathLastLtX edgePathLastLteX edgePathMax edgePathMin edgePathSum edgeSubtreeAND edgeSubtreeMax edgeSubtreeMin edgeSubtreeSum isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodeNearestAncestorGtX nodeNearestAncestorGteX nodeNearestAncestorLtX nodeNearestAncestorLteX nodePathAND nodePathFirstGtX nodePathFirstGteX nodePathFirstLtX nodePathFirstLteX nodePathLastGtX nodePathLastGteX nodePathLastLtX nodePathLastLteX nodePathMax nodePathMin nodePathSum nodeSubtreeAND nodeSubtreeMax nodeSubtreeMin nodeSubtreeSum parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: seg-tree
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeAdd: log(N)
#   edgeAssign: log(N)
#   edgeChmax: log(N)
#   edgeChmin: log(N)
#   edgeGet: log(N)
#   edgeNearestAncestorGtX: log^2(N)
#   edgeNearestAncestorGteX: log^2(N)
#   edgeNearestAncestorLtX: log^2(N)
#   edgeNearestAncestorLteX: log^2(N)
#   edgePathAND: log^2(N)
#   edgePathFirstGtX: log^2(N)
#   edgePathFirstGteX: log^2(N)
#   edgePathFirstLtX: log^2(N)
#   edgePathFirstLteX: log^2(N)
#   edgePathLastGtX: log^2(N)
#   edgePathLastGteX: log^2(N)
#   edgePathLastLtX: log^2(N)
#   edgePathLastLteX: log^2(N)
#   edgePathMax: log^2(N)
#   edgePathMin: log^2(N)
#   edgePathSum: log^2(N)
#   edgeSubtreeAND: log(N)
#   edgeSubtreeMax: log(N)
#   edgeSubtreeMin: log(N)
#   edgeSubtreeSum: log(N)
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
#   nodeAdd: log(N)
#   nodeAssign: log(N)
#   nodeChmax: log(N)
#   nodeChmin: log(N)
#   nodeGet: log(N)
#   nodeNearestAncestorGtX: log^2(N)
#   nodeNearestAncestorGteX: log^2(N)
#   nodeNearestAncestorLtX: log^2(N)
#   nodeNearestAncestorLteX: log^2(N)
#   nodePathAND: log^2(N)
#   nodePathFirstGtX: log^2(N)
#   nodePathFirstGteX: log^2(N)
#   nodePathFirstLtX: log^2(N)
#   nodePathFirstLteX: log^2(N)
#   nodePathLastGtX: log^2(N)
#   nodePathLastGteX: log^2(N)
#   nodePathLastLtX: log^2(N)
#   nodePathLastLteX: log^2(N)
#   nodePathMax: log^2(N)
#   nodePathMin: log^2(N)
#   nodePathSum: log^2(N)
#   nodeSubtreeAND: log(N)
#   nodeSubtreeMax: log(N)
#   nodeSubtreeMin: log(N)
#   nodeSubtreeSum: log(N)
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: log(N)
#   pathNodes: K+log(N)
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: log(N)
#   unweightedDistBetweenPaths: log(N)
#   unweightedDistToPath: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[4*N] mn[4*N] mx[4*N] an[4*N]
#   tags: none
#   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: leaves [n, 2n) hold each value's own aggregates

# Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
# its sum, its min, its max, its AND over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1
# when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s =
# its level); an update rewrites a leaf, then its ancestors.

INF, NEG = float("inf"), float("-inf")


class SegTree:
    __slots__ = ('n', 'h', 'sm', 'mn', 'mx', 'an')


    # O(N) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.mn = [0] * n + list(arr)
        self.mx = [0] * n + list(arr)
        self.an = [0] * n + list(arr)
        for x in range(n - 1, 0, -1):
            self._pull(x)

    # O(N) -- the whole array
    def getAll(self):
        return self.sm[self.n:]

    # O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] > x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] >= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] >= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] < x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] < x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] <= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] <= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, self._leaf(p) + v)
        self._rebuild(p)

    # O(logN) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        return self._leaf(p)

    # O(logN) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeAndQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAndQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, an = self.n, self.an
        res, lo, hi = -1, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res &= an[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res &= an[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, mx = self.n, self.mx
        res, lo, hi = NEG, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                if mx[lo] > res:
                    res = mx[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                if mx[hi] > res:
                    res = mx[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, mn = self.n, self.mn
        res, lo, hi = INF, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                if mn[lo] < res:
                    res = mn[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                if mn[hi] < res:
                    res = mn[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm = self.n, self.sm
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res += sm[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res += sm[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] > x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] >= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] >= x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] < x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] < x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] <= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] <= x else 2 * t
                return t - n
        return -1

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)

    # O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.n < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.n - 1)

    # O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.n < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.n - 1)

    # O(log(N)) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def andAll(self):
        if self.n < 1:
            raise IndexError("andAll: needs n >= 1")
        return self.rangeAndQuery(0, self.n - 1)

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.mn[p] = v
        self.mx[p] = v
        self.an[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x):  # recompute node x from its children
        a, b = 2 * x, 2 * x + 1
        self.sm[x] = self.sm[a] + self.sm[b]
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w
        self.an[x] = self.an[a] & self.an[b]

    def _rebuild(self, p):  # recompute every ancestor of leaf p
        while p > 1:
            p >>= 1
            self._pull(p)

    def _nodes(self, l, r):  # the O(logN) nodes covering a[l..r], left to right, each with its level
        n = self.n
        lo, hi, s, left, right = l + n, r + n + 1, 0, [], []
        while lo < hi:
            if lo & 1:
                left.append((lo, s))
                lo += 1
            if hi & 1:
                hi -= 1
                right.append((hi, s))
            lo >>= 1
            hi >>= 1
            s += 1
        return left + right[::-1]


from bisect import bisect_left


# tree = Tree(edges, root, vals)
#
# edges: the tree's n - 1 edges with their weights. Whether nodes are 0..n-1 or 1..n is detected automatically from
#        the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b, w), ...]     e.g. [(0, 1, 5), (1, 2, 7)]
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
#
#   Tree([(0, 1, 5), (1, 2, 7)], 0, [10, 20, 30])       # nodes 0..2, rooted at 0
#   Tree([(1, 2, 5), (2, 3, 7)], 1, [0, 10, 20, 30])    # nodes 1..3, rooted at 1
#
# The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each other. For
# nodes, a path a..b includes both a and b. For edges, a path a..b covers the edges between a and b and a subtree the
# edges below node; an edge is named by its two ends in either order, a search that finds an edge returns its lower end
# (the end farther from the root), and a query with no edges to look at (a path a..a, a leaf's subtree) says what it
# returns. Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree raises
# IndexError. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (SegTree) sit
# over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's weight at its lower end's
# position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n) ranges, one per chain it
# crosses.
class Tree:
    # O(n) -- builds the layout and the two range structures; raises ValueError when the edges are not one tree on nodes
    # 0..n-1 or 1..n, an edge has no weight, or vals has the wrong length
    def __init__(self, edges, root, vals):
        n = len(edges) + 1
        lo = float("inf")
        for e in edges:
            if len(e) != 2 and len(e) != 3:
                raise ValueError(f"Tree: every edge needs 2 or 3 numbers, (a, b) or (a, b, w), got {e}")
            if e[0] < lo:
                lo = e[0]
            if e[1] < lo:
                lo = e[1]
        if not edges:
            lo = root
        if lo != 0 and lo != 1:
            raise ValueError(f"Tree: nodes must be labeled 0..n-1 or 1..n, but the smallest label is {lo}")
        hi = lo + n - 1
        if not lo <= root <= hi:
            raise ValueError(f"Tree: root must be one of the nodes {lo}..{hi}, got {root}")
        adj = [[] for _ in range(hi + 1)]
        for e in edges:
            a, b = e[0], e[1]
            if a > hi or b > hi:
                raise ValueError(f"Tree: {n - 1} edges means the nodes are {lo}..{hi}, got the edge ({a}, {b})")
            adj[a].append(b)
            adj[b].append(a)

        # parents and depths, top down (par is -2 until a node is reached)
        par = [-2] * (hi + 1)
        dep = [0] * (hi + 1)
        par[root] = -1
        bfs = [root]
        for v in bfs:
            d = dep[v] + 1
            for u in adj[v]:
                if par[u] == -2:
                    par[u] = v
                    dep[u] = d
                    bfs.append(u)
        if len(bfs) != n:
            raise ValueError("Tree: the edges do not form one tree (some node cannot be reached from root)")

        # subtree sizes bottom up, then each node's heavy child (the one with the biggest subtree)
        sz = [1] * (hi + 1)
        for i in range(n - 1, 0, -1):
            v = bfs[i]
            sz[par[v]] += sz[v]
        heavy = [-1] * (hi + 1)
        for i in range(1, n):
            v = bfs[i]
            p = par[v]
            if heavy[p] == -1 or sz[v] > sz[heavy[p]]:
                heavy[p] = v

        # positions: a preorder that always steps into the heavy child first, so a heavy chain is one stretch
        head = [0] * (hi + 1)  # the top node of each node's chain
        pos = [0] * (hi + 1)
        order = [0] * n  # order[pos[v]] = v
        head[root] = root
        stack = [root]
        t = 0
        while stack:
            v = stack.pop()
            pos[v] = t
            order[t] = v
            t += 1
            h = heavy[v]
            p = par[v]
            for u in adj[v]:
                if u != p and u != h:
                    head[u] = u
                    stack.append(u)
            if h != -1:  # pushed last, so it is popped next
                head[h] = head[v]
                stack.append(h)

        # depthPos[depthStart[d] : depthStart[d + 1]] = the positions of the nodes at depth d, increasing
        maxDep = dep[bfs[-1]]
        depthStart = [0] * (maxDep + 2)
        for v in bfs:
            depthStart[dep[v] + 1] += 1
        for d in range(maxDep + 1):
            depthStart[d + 1] += depthStart[d]
        at = depthStart[:]
        depthPos = [0] * n
        for i in range(n):
            d = dep[order[i]]
            depthPos[at[d]] = i
            at[d] += 1

        self.n, self.lo, self.hi, self.root = n, lo, hi, root
        self.par, self.dep, self.sz, self.head, self.pos, self.order = par, dep, sz, head, pos, order
        self.depthStart, self.depthPos = depthStart, depthPos
        if len(vals) != hi + 1:
            raise ValueError(f"Tree: vals[node] is node's value, so nodes {lo}..{hi} need len(vals) = {hi + 1}"
                             f"{' (vals[0] is ignored)' if lo else ''}, got {len(vals)}")
        for e in edges:
            if len(e) != 3:
                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")
        arr = [edges[0][2] if edges else 0] * n  # (position 0 is the root's: it holds no edge, never read)
        for e in edges:
            a, b = e[0], e[1]
            arr[pos[a] if par[a] == b else pos[b]] = e[2]
        self.nodeSeg = SegTree([vals[v] for v in order])  # the node values, in position order
        self.edgeSeg = SegTree(arr)  # each edge's weight, at its lower end's position

    # O(log n) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.nodeSeg.pointGet(self.pos[node])

    # O(log n) -- val(node) = x
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        self.nodeSeg.pointAssign(self.pos[node], x)

    # O(log n) -- val(node) += x
    def nodeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAdd", node)
        self.nodeSeg.pointAdd(self.pos[node], x)

    # O(log n) -- val(node) = max(val, x)
    def nodeChmax(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmax", node)
        self.nodeSeg.pointChmax(self.pos[node], x)

    # O(log n) -- val(node) = min(val, x)
    def nodeChmin(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmin", node)
        self.nodeSeg.pointChmin(self.pos[node], x)

    # O(log^2 n) -- sum of the node values on the path a..b
    def nodePathSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSum", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeSum
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r)
        return res

    # O(log^2 n) -- min node value on the path a..b
    def nodePathMin(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMin", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeMin
        res = float("inf")
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a])
            if v < res:
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r)
        if v < res:
            res = v
        return res

    # O(log^2 n) -- max node value on the path a..b
    def nodePathMax(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMax", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeMax
        res = float("-inf")
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a])
            if v > res:
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r)
        if v > res:
            res = v
        return res

    # O(log^2 n) -- AND of the node values on the path a..b
    def nodePathAND(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathAND", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeAndQuery
        res = -1
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res &= query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res &= query(l, r)
        return res

    # O(log^2 n) -- nearest ancestor of node (node included) with val >= x (-1 if none)
    def nodeNearestAncestorGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeNearestAncestorGteX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.nodeSeg.rightmostGteX
        while node != -1:
            i = find(pos[head[node]], pos[node], x)
            if i != -1:
                return self.order[i]
            node = par[head[node]]
        return -1

    def _nodeFirstGteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.nodeSeg.leftmostGteX, self.nodeSeg.rightmostGteX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        else:
            l, r = pos[a], pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first node walking a -> b with val >= x (-1 if none)
    def nodePathFirstGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstGteX", a, b)
        return self._nodeFirstGteX(a, b, x)

    # O(log^2 n) -- last node walking a -> b with val >= x (-1 if none)
    def nodePathLastGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastGteX", a, b)
        return self._nodeFirstGteX(b, a, x)

    # O(log^2 n) -- nearest ancestor of node (node included) with val > x (-1 if none)
    def nodeNearestAncestorGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeNearestAncestorGtX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.nodeSeg.rightmostGtX
        while node != -1:
            i = find(pos[head[node]], pos[node], x)
            if i != -1:
                return self.order[i]
            node = par[head[node]]
        return -1

    def _nodeFirstGtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.nodeSeg.leftmostGtX, self.nodeSeg.rightmostGtX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        else:
            l, r = pos[a], pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first node walking a -> b with val > x (-1 if none)
    def nodePathFirstGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstGtX", a, b)
        return self._nodeFirstGtX(a, b, x)

    # O(log^2 n) -- last node walking a -> b with val > x (-1 if none)
    def nodePathLastGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastGtX", a, b)
        return self._nodeFirstGtX(b, a, x)

    # O(log^2 n) -- nearest ancestor of node (node included) with val <= x (-1 if none)
    def nodeNearestAncestorLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeNearestAncestorLteX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.nodeSeg.rightmostLteX
        while node != -1:
            i = find(pos[head[node]], pos[node], x)
            if i != -1:
                return self.order[i]
            node = par[head[node]]
        return -1

    def _nodeFirstLteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.nodeSeg.leftmostLteX, self.nodeSeg.rightmostLteX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        else:
            l, r = pos[a], pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first node walking a -> b with val <= x (-1 if none)
    def nodePathFirstLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstLteX", a, b)
        return self._nodeFirstLteX(a, b, x)

    # O(log^2 n) -- last node walking a -> b with val <= x (-1 if none)
    def nodePathLastLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastLteX", a, b)
        return self._nodeFirstLteX(b, a, x)

    # O(log^2 n) -- nearest ancestor of node (node included) with val < x (-1 if none)
    def nodeNearestAncestorLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeNearestAncestorLtX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.nodeSeg.rightmostLtX
        while node != -1:
            i = find(pos[head[node]], pos[node], x)
            if i != -1:
                return self.order[i]
            node = par[head[node]]
        return -1

    def _nodeFirstLtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.nodeSeg.leftmostLtX, self.nodeSeg.rightmostLtX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        else:
            l, r = pos[a], pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first node walking a -> b with val < x (-1 if none)
    def nodePathFirstLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstLtX", a, b)
        return self._nodeFirstLtX(a, b, x)

    # O(log^2 n) -- last node walking a -> b with val < x (-1 if none)
    def nodePathLastLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastLtX", a, b)
        return self._nodeFirstLtX(b, a, x)

    # O(log n) -- sum of the node values in node's subtree
    def nodeSubtreeSum(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSum", node)
        l = self.pos[node]
        return self.nodeSeg.rangeSum(l, l + self.sz[node] - 1)

    # O(log n) -- min node value in node's subtree
    def nodeSubtreeMin(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMin", node)
        l = self.pos[node]
        return self.nodeSeg.rangeMin(l, l + self.sz[node] - 1)

    # O(log n) -- max node value in node's subtree
    def nodeSubtreeMax(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMax", node)
        l = self.pos[node]
        return self.nodeSeg.rangeMax(l, l + self.sz[node] - 1)

    # O(log n) -- AND of the node values in node's subtree
    def nodeSubtreeAND(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeAND", node)
        l = self.pos[node]
        return self.nodeSeg.rangeAndQuery(l, l + self.sz[node] - 1)

    # the position that holds the edge a - b: its lower end's (a and b in either order)
    def _edge(self, name, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad(name, a, b)
        if self.par[a] == b:
            return self.pos[a]
        if self.par[b] == a:
            return self.pos[b]
        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")

    # O(log n) -- weight(a - b); a and b are the edge's two ends, in either order
    def edgeGet(self, a, b):
        return self.edgeSeg.pointGet(self._edge("edgeGet", a, b))

    # O(log n) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    def edgeAssign(self, a, b, w):
        self.edgeSeg.pointAssign(self._edge("edgeAssign", a, b), w)

    # O(log n) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    def edgeAdd(self, a, b, w):
        self.edgeSeg.pointAdd(self._edge("edgeAdd", a, b), w)

    # O(log n) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    def edgeChmax(self, a, b, w):
        self.edgeSeg.pointChmax(self._edge("edgeChmax", a, b), w)

    # O(log n) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    def edgeChmin(self, a, b, w):
        self.edgeSeg.pointChmin(self._edge("edgeChmin", a, b), w)

    # O(log^2 n) -- sum of the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSum", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeSum
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r)
        return res

    # O(log^2 n) -- min edge weight on the path a..b; inf when a == b (no edges)
    def edgePathMin(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMin", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeMin
        res = float("inf")
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a])
            if v < res:
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r)
            if v < res:
                res = v
        return res

    # O(log^2 n) -- max edge weight on the path a..b; -inf when a == b (no edges)
    def edgePathMax(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMax", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeMax
        res = float("-inf")
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a])
            if v > res:
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r)
            if v > res:
                res = v
        return res

    # O(log^2 n) -- AND of the edge weights on the path a..b; -1 (every bit set) when a == b (no edges)
    def edgePathAND(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathAND", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeAndQuery
        res = -1
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res &= query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res &= query(l + 1, r)
        return res

    # O(log^2 n) -- nearest edge above node (toward the root) with weight >= x, as its lower end (-1 if none)
    def edgeNearestAncestorGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeNearestAncestorGteX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.edgeSeg.rightmostGteX
        while node != -1:
            l = pos[head[node]] or 1  # (position 0 is the root's: it holds no edge)
            if l <= pos[node]:
                i = find(l, pos[node], x)
                if i != -1:
                    return self.order[i]
            node = par[head[node]]
        return -1

    def _edgeFirstGteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.edgeSeg.leftmostGteX, self.edgeSeg.rightmostGteX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first edge walking a -> b with weight >= x, as its lower end (-1 if none)
    def edgePathFirstGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstGteX", a, b)
        return self._edgeFirstGteX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b with weight >= x, as its lower end (-1 if none)
    def edgePathLastGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastGteX", a, b)
        return self._edgeFirstGteX(b, a, x)

    # O(log^2 n) -- nearest edge above node (toward the root) with weight > x, as its lower end (-1 if none)
    def edgeNearestAncestorGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeNearestAncestorGtX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.edgeSeg.rightmostGtX
        while node != -1:
            l = pos[head[node]] or 1  # (position 0 is the root's: it holds no edge)
            if l <= pos[node]:
                i = find(l, pos[node], x)
                if i != -1:
                    return self.order[i]
            node = par[head[node]]
        return -1

    def _edgeFirstGtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.edgeSeg.leftmostGtX, self.edgeSeg.rightmostGtX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first edge walking a -> b with weight > x, as its lower end (-1 if none)
    def edgePathFirstGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstGtX", a, b)
        return self._edgeFirstGtX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b with weight > x, as its lower end (-1 if none)
    def edgePathLastGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastGtX", a, b)
        return self._edgeFirstGtX(b, a, x)

    # O(log^2 n) -- nearest edge above node (toward the root) with weight <= x, as its lower end (-1 if none)
    def edgeNearestAncestorLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeNearestAncestorLteX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.edgeSeg.rightmostLteX
        while node != -1:
            l = pos[head[node]] or 1  # (position 0 is the root's: it holds no edge)
            if l <= pos[node]:
                i = find(l, pos[node], x)
                if i != -1:
                    return self.order[i]
            node = par[head[node]]
        return -1

    def _edgeFirstLteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.edgeSeg.leftmostLteX, self.edgeSeg.rightmostLteX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first edge walking a -> b with weight <= x, as its lower end (-1 if none)
    def edgePathFirstLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstLteX", a, b)
        return self._edgeFirstLteX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b with weight <= x, as its lower end (-1 if none)
    def edgePathLastLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastLteX", a, b)
        return self._edgeFirstLteX(b, a, x)

    # O(log^2 n) -- nearest edge above node (toward the root) with weight < x, as its lower end (-1 if none)
    def edgeNearestAncestorLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeNearestAncestorLtX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.edgeSeg.rightmostLtX
        while node != -1:
            l = pos[head[node]] or 1  # (position 0 is the root's: it holds no edge)
            if l <= pos[node]:
                i = find(l, pos[node], x)
                if i != -1:
                    return self.order[i]
            node = par[head[node]]
        return -1

    def _edgeFirstLtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.edgeSeg.leftmostLtX, self.edgeSeg.rightmostLtX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first edge walking a -> b with weight < x, as its lower end (-1 if none)
    def edgePathFirstLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstLtX", a, b)
        return self._edgeFirstLtX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b with weight < x, as its lower end (-1 if none)
    def edgePathLastLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastLtX", a, b)
        return self._edgeFirstLtX(b, a, x)

    # O(log n) -- sum of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeSum(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeSum", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.rangeSum(l, r)

    # O(log n) -- min edge weight in node's subtree; inf when node is a leaf (no edges)
    def edgeSubtreeMin(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMin", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return float("inf")
        return self.edgeSeg.rangeMin(l, r)

    # O(log n) -- max edge weight in node's subtree; -inf when node is a leaf (no edges)
    def edgeSubtreeMax(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMax", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return float("-inf")
        return self.edgeSeg.rangeMax(l, r)

    # O(log n) -- AND of the edge weights in node's subtree; -1 (every bit set) when node is a leaf (no edges)
    def edgeSubtreeAND(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeAND", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return -1
        return self.edgeSeg.rangeAndQuery(l, r)

    def _bad(self, name, *nodes):
        raise IndexError(f"{name}: needs {self.lo} <= node <= {self.hi}, got {', '.join(map(str, nodes))}")

    def _lca(self, a, b):
        head, par, dep = self.head, self.par, self.dep
        while head[a] != head[b]:
            if dep[head[a]] > dep[head[b]]:
                a = par[head[a]]
            else:
                b = par[head[b]]
        return a if dep[a] < dep[b] else b

    # the node k steps above node (k <= its depth): a whole chain at a time
    def _kth(self, node, k):
        head, pos, par = self.head, self.pos, self.par
        while True:
            h = head[node]
            d = pos[node] - pos[h]
            if k <= d:
                return self.order[pos[node] - k]
            k -= d + 1
            node = par[h]

    def _dist(self, a, b):
        dep = self.dep
        return dep[a] + dep[b] - 2 * dep[self._lca(a, b)]

    # of the three pairwise lcas two are equal and the third, the deeper one, is the median
    def _median(self, a, b, c):
        dep = self.dep
        x, y, z = self._lca(a, b), self._lca(a, c), self._lca(b, c)
        if dep[y] > dep[x]:
            x = y
        return z if dep[z] > dep[x] else x

    def _isAncestor(self, a, b):
        return self.pos[a] <= self.pos[b] < self.pos[a] + self.sz[a]

    def _onPath(self, a, b, node):
        return self._isAncestor(self._lca(a, b), node) and (self._isAncestor(node, a) or self._isAncestor(node, b))

    # the neighbor of a on the way to b (a != b): the child holding b when b is below a, else a's parent
    def _next(self, a, b):
        if self._isAncestor(a, b):
            return self._kth(b, self.dep[b] - self.dep[a] - 1)
        return self.par[a]

    # O(log n) -- lowest common ancestor of a and b
    def lca(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lca", a, b)
        return self._lca(a, b)

    # O(log n) -- number of edges on the path a..b
    def unweightedDist(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("unweightedDist", a, b)
        return self.dep[a] + self.dep[b] - 2 * self.dep[self._lca(a, b)]

    # O(1) -- edges from the root to node (the root is depth 0)
    def depth(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("depth", node)
        return self.dep[node]

    # O(1) -- node's parent (-1 for the root)
    def parent(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("parent", node)
        return self.par[node]

    # O(log n) -- the node k steps above node (k = 0 is node itself; -1 if that is past the root); needs k >= 0
    def kthAncestor(self, node, k):
        if not self.lo <= node <= self.hi:
            self._bad("kthAncestor", node)
        if k < 0:
            raise IndexError(f"kthAncestor: needs k >= 0, got {k}")
        return self._kth(node, k) if k <= self.dep[node] else -1

    # O(1) -- is a an ancestor of b? (True when a == b)
    def isAncestor(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("isAncestor", a, b)
        return self.pos[a] <= self.pos[b] < self.pos[a] + self.sz[a]

    # O(1) -- number of nodes in node's subtree (node included)
    def subtreeSize(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("subtreeSize", node)
        return self.sz[node]

    # O(log n) -- number of nodes in node's subtree at depth d (the root is depth 0); 0 when there are none
    def countAtDepthInSubtree(self, node, d):
        if not self.lo <= node <= self.hi:
            self._bad("countAtDepthInSubtree", node)
        if d < 0 or d + 1 >= len(self.depthStart):
            return 0
        s, e = self.depthStart[d], self.depthStart[d + 1]
        l = self.pos[node]
        return bisect_left(self.depthPos, l + self.sz[node], s, e) - bisect_left(self.depthPos, l, s, e)

    # O(log n) -- lca of a and b if the tree were rooted at r instead
    def lcaRootedAt(self, r, a, b):
        if not (self.lo <= r <= self.hi and self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lcaRootedAt", r, a, b)
        return self._median(a, b, r)

    # O(log n) -- node's parent if the tree were rooted at r (-1 when node == r)
    def parentRootedAt(self, r, node):
        if not (self.lo <= r <= self.hi and self.lo <= node <= self.hi):
            self._bad("parentRootedAt", r, node)
        return -1 if node == r else self._next(node, r)

    # O(log n) -- size of node's subtree if the tree were rooted at r
    def subtreeSizeRootedAt(self, r, node):
        if not (self.lo <= r <= self.hi and self.lo <= node <= self.hi):
            self._bad("subtreeSizeRootedAt", r, node)
        if node == r:
            return self.n
        if self._isAncestor(node, r):  # r hangs below node: everything but the child holding r
            return self.n - self.sz[self._kth(r, self.dep[r] - self.dep[node] - 1)]
        return self.sz[node]

    # O(log n) -- the kth node walking a -> b (k = 0 is a, k = unweightedDist(a, b) is b; -1 if k is past b); needs
    # k >= 0
    def kthNodeOnPath(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("kthNodeOnPath", a, b)
        if k < 0:
            raise IndexError(f"kthNodeOnPath: needs k >= 0, got {k}")
        dep = self.dep
        c = self._lca(a, b)
        up = dep[a] - dep[c]
        total = up + dep[b] - dep[c]
        if k > total:
            return -1
        return self._kth(a, k) if k <= up else self._kth(b, total - k)

    # O(log n) -- the neighbor of a one step toward b (-1 if a == b)
    def nextNodeOnPath(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nextNodeOnPath", a, b)
        return -1 if a == b else self._next(a, b)

    # O(log n) -- does the path a..b pass through node? (a and b count)
    def isOnPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("isOnPath", a, b, node)
        return self._onPath(a, b, node)

    # O(log n) -- fewest edges from node to any node on the path a..b (0 if node is on it)
    def unweightedDistToPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("unweightedDistToPath", a, b, node)
        return self._dist(node, self._median(a, b, node))

    # O(log n) -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    def unweightedDistBetweenPaths(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("unweightedDistBetweenPaths", a, b, c, d)
        p = self._median(a, b, c)  # where c's side meets the path a..b
        if p != self._median(a, b, d):
            return 0  # c and d meet it at different nodes, so c..d runs along it
        return self._dist(p, self._median(c, d, p))

    # O(log n) -- the one node that lies on all three paths between a, b and c
    def median(self, a, b, c):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= c <= self.hi):
            self._bad("median", a, b, c)
        return self._median(a, b, c)

    # O(log n) -- the shared part of paths a..b and c..d as its two end nodes (p, q), p first walking a -> b; p == q
    # if they share one node; (-1, -1) if they share none
    def pathIntersection(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("pathIntersection", a, b, c, d)
        p, q = self._median(a, b, c), self._median(a, b, d)  # where c's side and d's side meet the path a..b
        if p == q:
            return (p, p) if self._onPath(c, d, p) else (-1, -1)
        return (p, q) if self._dist(a, p) < self._dist(a, q) else (q, p)

    # O(K + log n) -- every node on the path a..b, in order from a (K = how many)
    def pathNodes(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("pathNodes", a, b)
        par = self.par
        c = self._lca(a, b)
        out = []
        while a != c:
            out.append(a)
            a = par[a]
        out.append(c)
        tail = []
        while b != c:
            tail.append(b)
            b = par[b]
        tail.reverse()
        return out + tail
