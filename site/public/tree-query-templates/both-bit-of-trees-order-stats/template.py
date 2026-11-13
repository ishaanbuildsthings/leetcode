# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-bit-of-trees-order-stats/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/bit-of-trees-order-stats/template.py
# @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgePathCountGtX edgePathCountGteX edgePathCountInValRange edgePathCountLtX edgePathCountLteX edgePathCountOccurrences edgePathLargestLtX edgePathLargestLteX edgePathMax edgePathMin edgePathSmallestGtX edgePathSmallestGteX edgeSubtreeCountGtX edgeSubtreeCountGteX edgeSubtreeCountInValRange edgeSubtreeCountLtX edgeSubtreeCountLteX edgeSubtreeCountOccurrences edgeSubtreeKthSmallest edgeSubtreeLargestLtX edgeSubtreeLargestLteX edgeSubtreeMax edgeSubtreeMin edgeSubtreeSmallestGtX edgeSubtreeSmallestGteX isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathCountGtX nodePathCountGteX nodePathCountInValRange nodePathCountLtX nodePathCountLteX nodePathCountOccurrences nodePathLargestLtX nodePathLargestLteX nodePathMax nodePathMin nodePathSmallestGtX nodePathSmallestGteX nodeSubtreeCountGtX nodeSubtreeCountGteX nodeSubtreeCountInValRange nodeSubtreeCountLtX nodeSubtreeCountLteX nodeSubtreeCountOccurrences nodeSubtreeKthSmallest nodeSubtreeLargestLtX nodeSubtreeLargestLteX nodeSubtreeMax nodeSubtreeMin nodeSubtreeSmallestGtX nodeSubtreeSmallestGteX parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: bit-of-trees
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeAdd: log(N)*log(U)
#   edgeAssign: log(N)*log(U)
#   edgeChmax: log(N)*log(U)
#   edgeChmin: log(N)*log(U)
#   edgeGet: 1
#   edgePathCountGtX: log^2(N)*log(U)
#   edgePathCountGteX: log^2(N)*log(U)
#   edgePathCountInValRange: log^2(N)*log(U)
#   edgePathCountLtX: log^2(N)*log(U)
#   edgePathCountLteX: log^2(N)*log(U)
#   edgePathCountOccurrences: log^2(N)*log(U)
#   edgePathLargestLtX: log^2(N)*log(U)
#   edgePathLargestLteX: log^2(N)*log(U)
#   edgePathMax: log^2(N)*log(U)
#   edgePathMin: log^2(N)*log(U)
#   edgePathSmallestGtX: log^2(N)*log(U)
#   edgePathSmallestGteX: log^2(N)*log(U)
#   edgeSubtreeCountGtX: log(N)*log(U)
#   edgeSubtreeCountGteX: log(N)*log(U)
#   edgeSubtreeCountInValRange: log(N)*log(U)
#   edgeSubtreeCountLtX: log(N)*log(U)
#   edgeSubtreeCountLteX: log(N)*log(U)
#   edgeSubtreeCountOccurrences: log(N)*log(U)
#   edgeSubtreeKthSmallest: log(N)*log(U)
#   edgeSubtreeLargestLtX: log(N)*log(U)
#   edgeSubtreeLargestLteX: log(N)*log(U)
#   edgeSubtreeMax: log(N)*log(U)
#   edgeSubtreeMin: log(N)*log(U)
#   edgeSubtreeSmallestGtX: log(N)*log(U)
#   edgeSubtreeSmallestGteX: log(N)*log(U)
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
#   nodeAdd: log(N)*log(U)
#   nodeAssign: log(N)*log(U)
#   nodeChmax: log(N)*log(U)
#   nodeChmin: log(N)*log(U)
#   nodeGet: 1
#   nodePathCountGtX: log^2(N)*log(U)
#   nodePathCountGteX: log^2(N)*log(U)
#   nodePathCountInValRange: log^2(N)*log(U)
#   nodePathCountLtX: log^2(N)*log(U)
#   nodePathCountLteX: log^2(N)*log(U)
#   nodePathCountOccurrences: log^2(N)*log(U)
#   nodePathLargestLtX: log^2(N)*log(U)
#   nodePathLargestLteX: log^2(N)*log(U)
#   nodePathMax: log^2(N)*log(U)
#   nodePathMin: log^2(N)*log(U)
#   nodePathSmallestGtX: log^2(N)*log(U)
#   nodePathSmallestGteX: log^2(N)*log(U)
#   nodeSubtreeCountGtX: log(N)*log(U)
#   nodeSubtreeCountGteX: log(N)*log(U)
#   nodeSubtreeCountInValRange: log(N)*log(U)
#   nodeSubtreeCountLtX: log(N)*log(U)
#   nodeSubtreeCountLteX: log(N)*log(U)
#   nodeSubtreeCountOccurrences: log(N)*log(U)
#   nodeSubtreeKthSmallest: log(N)*log(U)
#   nodeSubtreeLargestLtX: log(N)*log(U)
#   nodeSubtreeLargestLteX: log(N)*log(U)
#   nodeSubtreeMax: log(N)*log(U)
#   nodeSubtreeMin: log(N)*log(U)
#   nodeSubtreeSmallestGtX: log(N)*log(U)
#   nodeSubtreeSmallestGteX: log(N)*log(U)
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: log(N)
#   pathNodes: K+log(N)
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: log(N)
#   unweightedDistBetweenPaths: log(N)
#   unweightedDistToPath: log(N)
#   build: N*log(N)*log(U)
# @memory:
#   layout: none
#   node: L[2*N*log(N)*log(U)] R[2*N*log(N)*log(U)] C[2*N*log(N)*log(U)]
#   tags: none
#   other: root[2*N] arr[2*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: BIT over positions, each BIT node a dynamic value seg tree over [valLo, valHi] (U = its size); nodes are never freed, so each point update adds up to 2 log N log U of them

# a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over positions: BIT node j is a dynamic value
# seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the BIT
# prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
# subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.


class DynamicOrderStats:
    __slots__ = ('arr', 'n', 'vlo', 'vhi', 'root', 'L', 'R', 'C')

    # O(N log N log U) -- arr: the initial array (a list), 0-indexed; every value a[i] ever holds must lie in
    # [valLo, valHi] (any integers, negative is fine; U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        self.arr = list(arr)
        self.n = len(arr)
        self.vlo, self.vhi = valLo, valHi
        self.root = [0] * (self.n + 1)  # BIT node j's value tree (0: empty)
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
        for i, v in enumerate(arr):
            self._add(i, v, 1)

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.arr[i]

    # O(N) -- the whole array (a copy)
    def getAll(self):
        return list(self.arr)

    # O(logN logU) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        old = self.arr[i]
        if v != old:
            self._add(i, old, -1)
            self._add(i, v, 1)
            self.arr[i] = v

    # O(logN logU) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + v)

    # O(logN logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, max(self.pointGet(i), v))

    # O(logN logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, min(self.pointGet(i), v))

    # O(logN * logU) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self.countInValRange(l, r, x, x)

    # O(logN * logU) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else IndexError
    def countInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countInValRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if lowVal > highVal:
            return 0
        return self._countBelow(l, r, highVal + 1) - self._countBelow(l, r, lowVal)

    # O(logN * logU) -- # of values < x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._countBelow(l, r, x)

    # O(logN * logU) -- # of values <= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._countBelow(l, r, x + 1)

    # O(logN * logU) -- # of values > x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return r - l + 1 - self._countBelow(l, r, x + 1)

    # O(logN * logU) -- # of values >= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return r - l + 1 - self._countBelow(l, r, x)

    # O(logN * logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < n and 1 <= k <= r - l + 1,
    # else
    # IndexError
    def kthSmallest(self, l, r, k):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"kthSmallest: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logN * logU) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._kth(l, r, 1)

    # O(logN * logU) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._kth(l, r, r - l + 1)

    # O(logN * logU) -- smallest value >= x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def smallestGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"smallestGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, x)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN * logU) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def smallestGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"smallestGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, x + 1)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN * logU) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def largestLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"largestLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, x + 1)
        return None if c == 0 else self._kth(l, r, c)

    # O(logN * logU) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def largestLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"largestLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, x)
        return None if c == 0 else self._kth(l, r, c)

    # O(log(N)*log(U)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.n < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.n - 1)

    # O(log(N)*log(U)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.n < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.n - 1)

    # ---- internals ----

    # a[i] = v gains d copies in every BIT node covering i
    def _add(self, i, v, d):
        j = i + 1
        while j <= self.n:
            self.root[j] = self._ins(self.root[j], v, d)
            j += j & -j

    # (trees to add, trees to subtract) for a[l..r]
    def _sides(self, l, r):
        root, pos, neg = self.root, [], []
        j = r + 1
        while j:
            pos.append(root[j])
            j &= j - 1
        j = l
        while j:
            neg.append(root[j])
            j &= j - 1
        return pos, neg

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        return self._kthIn(*self._sides(l, r), k)

    # # of values < x in a[l..r]
    def _countBelow(self, l, r, x):
        if x <= self.vlo:
            return 0
        if x > self.vhi:
            return r - l + 1
        return self._belowIn(*self._sides(l, r), x)[0]

    # ---- internals: walks over the value trees in pos (added) and neg (subtracted) ----

    def _newNode(self):
        self.L.append(0), self.R.append(0), self.C.append(0)
        return len(self.C) - 1

    # tree t (0: a new one) with d more copies of v
    def _ins(self, t, v, d):
        L, R, C = self.L, self.R, self.C
        if not t:
            t = self._newNode()
        top, nl, nh = t, self.vlo, self.vhi
        while True:
            C[t] += d
            if nl == nh:
                return top
            mid = (nl + nh) >> 1
            if v <= mid:
                if not L[t]:
                    L[t] = self._newNode()
                t, nh = L[t], mid
            else:
                if not R[t]:
                    R[t] = self._newNode()
                t, nl = R[t], mid + 1

    def _total(self, pos, neg, A):
        return sum(A[t] for t in pos) - sum(A[t] for t in neg)

    # the k-th smallest value, 1 <= k <= the trees' count
    def _kthIn(self, pos, neg, k):
        L, R, C = self.L, self.R, self.C
        nl, nh = self.vlo, self.vhi
        while nl != nh:
            mid = (nl + nh) >> 1
            c = sum(C[L[t]] for t in pos) - sum(C[L[t]] for t in neg)
            if k <= c:
                pos, neg, nh = [L[t] for t in pos if L[t]], [L[t] for t in neg if L[t]], mid
            else:
                k -= c
                pos, neg, nl = [R[t] for t in pos if R[t]], [R[t] for t in neg if R[t]], mid + 1
        return nl

    # (# of values < x, their sum), valLo < x <= valHi
    def _belowIn(self, pos, neg, x):
        L, R, C = self.L, self.R, self.C
        nl, nh, cnt, sm = self.vlo, self.vhi, 0, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            if x <= mid:
                pos, neg, nh = [L[t] for t in pos if L[t]], [L[t] for t in neg if L[t]], mid
            else:  # the whole left half is below x
                cnt += sum(C[L[t]] for t in pos) - sum(C[L[t]] for t in neg)
                pos, neg, nl = [R[t] for t in pos if R[t]], [R[t] for t in neg if R[t]], mid + 1
        return cnt, sm


from bisect import bisect_left


# tree = Tree(edges, root, vals, valLo, valHi)
#
# edges: the tree's n - 1 edges with their weights. Whether nodes are 0..n-1 or 1..n is detected automatically from
#        the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b, w), ...]     e.g. [(0, 1, 5), (1, 2, 7)]
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
# valLo: every value ever held is >= valLo (any integer, negative is fine).
# valHi: every value ever held is <= valHi.
#
#   Tree([(0, 1, 5), (1, 2, 7)], 0, [10, 20, 30], valLo, valHi)       # nodes 0..2, rooted at 0
#   Tree([(1, 2, 5), (2, 3, 7)], 1, [0, 10, 20, 30], valLo, valHi)    # nodes 1..3, rooted at 1
#
# The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each other. For
# nodes, a path a..b includes both a and b. For edges, a path a..b covers the edges between a and b and a subtree the
# edges below node; an edge is named by its two ends in either order, a search that finds an edge returns its lower end
# (the end farther from the root), and a query with no edges to look at (a path a..a, a leaf's subtree) says what it
# returns. Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree raises
# IndexError. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above
# (DynamicOrderStats) sit over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's
# weight at its lower end's position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n)
# ranges, one per chain it crosses.
class Tree:
    # O(n * log n * log U) -- builds the layout and the two range structures; raises ValueError when the edges are not
    # one tree on nodes 0..n-1 or 1..n, an edge has no weight, or vals has the wrong length
    def __init__(self, edges, root, vals, valLo, valHi):
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
        self.nodeSeg = DynamicOrderStats([vals[v] for v in order], valLo, valHi)  # the node values, in position order
        self.edgeSeg = DynamicOrderStats(arr, valLo, valHi)  # each edge's weight, at its lower end's position

    # O(1) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.nodeSeg.pointGet(self.pos[node])

    # O(log n * log U) -- val(node) = x
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        self.nodeSeg.pointAssign(self.pos[node], x)

    # O(log n * log U) -- val(node) += x
    def nodeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAdd", node)
        self.nodeSeg.pointAdd(self.pos[node], x)

    # O(log n * log U) -- val(node) = max(val, x)
    def nodeChmax(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmax", node)
        self.nodeSeg.pointChmax(self.pos[node], x)

    # O(log n * log U) -- val(node) = min(val, x)
    def nodeChmin(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmin", node)
        self.nodeSeg.pointChmin(self.pos[node], x)

    # O(log^2 n * log U) -- min node value on the path a..b
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

    # O(log^2 n * log U) -- max node value on the path a..b
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

    # O(log^2 n * log U) -- how many node values on the path a..b are < x
    def nodePathCountLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.countLtX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^2 n * log U) -- how many node values on the path a..b are <= x
    def nodePathCountLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.countLteX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^2 n * log U) -- how many node values on the path a..b are > x
    def nodePathCountGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.countGtX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^2 n * log U) -- how many node values on the path a..b are >= x
    def nodePathCountGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.countGteX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^2 n * log U) -- how many node values on the path a..b are in [low, high]
    def nodePathCountInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountInValRange", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.countInValRange
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], low, high)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, low, high)
        return res

    # O(log^2 n * log U) -- smallest of the node values on the path a..b that is >= x (None if none)
    def nodePathSmallestGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSmallestGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.smallestGteX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v < res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r, x)
        if v is not None and (res is None or v < res):
            res = v
        return res

    # O(log^2 n * log U) -- smallest of the node values on the path a..b that is > x (None if none)
    def nodePathSmallestGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSmallestGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.smallestGtX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v < res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r, x)
        if v is not None and (res is None or v < res):
            res = v
        return res

    # O(log^2 n * log U) -- largest of the node values on the path a..b that is <= x (None if none)
    def nodePathLargestLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLargestLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.largestLteX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v > res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r, x)
        if v is not None and (res is None or v > res):
            res = v
        return res

    # O(log^2 n * log U) -- largest of the node values on the path a..b that is < x (None if none)
    def nodePathLargestLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLargestLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.largestLtX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v > res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r, x)
        if v is not None and (res is None or v > res):
            res = v
        return res

    # O(log^2 n * log U) -- how many node values on the path a..b equal x
    def nodePathCountOccurrences(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountOccurrences", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.countOccurrences
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log n * log U) -- min node value in node's subtree
    def nodeSubtreeMin(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMin", node)
        l = self.pos[node]
        return self.nodeSeg.rangeMin(l, l + self.sz[node] - 1)

    # O(log n * log U) -- max node value in node's subtree
    def nodeSubtreeMax(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMax", node)
        l = self.pos[node]
        return self.nodeSeg.rangeMax(l, l + self.sz[node] - 1)

    # O(log n * log U) -- kth smallest of the node values in node's subtree (1-indexed: k = 1 is the min)
    def nodeSubtreeKthSmallest(self, node, k):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeKthSmallest", node)
        l = self.pos[node]
        return self.nodeSeg.kthSmallest(l, l + self.sz[node] - 1, k)

    # O(log n * log U) -- how many node values in node's subtree are < x
    def nodeSubtreeCountLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountLtX", node)
        l = self.pos[node]
        return self.nodeSeg.countLtX(l, l + self.sz[node] - 1, x)

    # O(log n * log U) -- how many node values in node's subtree are <= x
    def nodeSubtreeCountLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountLteX", node)
        l = self.pos[node]
        return self.nodeSeg.countLteX(l, l + self.sz[node] - 1, x)

    # O(log n * log U) -- how many node values in node's subtree are > x
    def nodeSubtreeCountGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountGtX", node)
        l = self.pos[node]
        return self.nodeSeg.countGtX(l, l + self.sz[node] - 1, x)

    # O(log n * log U) -- how many node values in node's subtree are >= x
    def nodeSubtreeCountGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountGteX", node)
        l = self.pos[node]
        return self.nodeSeg.countGteX(l, l + self.sz[node] - 1, x)

    # O(log n * log U) -- how many node values in node's subtree are in [low, high]
    def nodeSubtreeCountInValRange(self, node, low, high):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountInValRange", node)
        l = self.pos[node]
        return self.nodeSeg.countInValRange(l, l + self.sz[node] - 1, low, high)

    # O(log n * log U) -- smallest of the node values in node's subtree that is >= x (None if none)
    def nodeSubtreeSmallestGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSmallestGteX", node)
        l = self.pos[node]
        return self.nodeSeg.smallestGteX(l, l + self.sz[node] - 1, x)

    # O(log n * log U) -- smallest of the node values in node's subtree that is > x (None if none)
    def nodeSubtreeSmallestGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSmallestGtX", node)
        l = self.pos[node]
        return self.nodeSeg.smallestGtX(l, l + self.sz[node] - 1, x)

    # O(log n * log U) -- largest of the node values in node's subtree that is <= x (None if none)
    def nodeSubtreeLargestLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeLargestLteX", node)
        l = self.pos[node]
        return self.nodeSeg.largestLteX(l, l + self.sz[node] - 1, x)

    # O(log n * log U) -- largest of the node values in node's subtree that is < x (None if none)
    def nodeSubtreeLargestLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeLargestLtX", node)
        l = self.pos[node]
        return self.nodeSeg.largestLtX(l, l + self.sz[node] - 1, x)

    # O(log n * log U) -- how many node values in node's subtree equal x
    def nodeSubtreeCountOccurrences(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountOccurrences", node)
        l = self.pos[node]
        return self.nodeSeg.countOccurrences(l, l + self.sz[node] - 1, x)

    # the position that holds the edge a - b: its lower end's (a and b in either order)
    def _edge(self, name, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad(name, a, b)
        if self.par[a] == b:
            return self.pos[a]
        if self.par[b] == a:
            return self.pos[b]
        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")

    # O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    def edgeGet(self, a, b):
        return self.edgeSeg.pointGet(self._edge("edgeGet", a, b))

    # O(log n * log U) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    def edgeAssign(self, a, b, w):
        self.edgeSeg.pointAssign(self._edge("edgeAssign", a, b), w)

    # O(log n * log U) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    def edgeAdd(self, a, b, w):
        self.edgeSeg.pointAdd(self._edge("edgeAdd", a, b), w)

    # O(log n * log U) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    def edgeChmax(self, a, b, w):
        self.edgeSeg.pointChmax(self._edge("edgeChmax", a, b), w)

    # O(log n * log U) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    def edgeChmin(self, a, b, w):
        self.edgeSeg.pointChmin(self._edge("edgeChmin", a, b), w)

    # O(log^2 n * log U) -- min edge weight on the path a..b; inf when a == b (no edges)
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

    # O(log^2 n * log U) -- max edge weight on the path a..b; -inf when a == b (no edges)
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

    # O(log^2 n * log U) -- how many edge weights on the path a..b are < x; 0 when a == b (no edges)
    def edgePathCountLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.countLtX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(log^2 n * log U) -- how many edge weights on the path a..b are <= x; 0 when a == b (no edges)
    def edgePathCountLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.countLteX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(log^2 n * log U) -- how many edge weights on the path a..b are > x; 0 when a == b (no edges)
    def edgePathCountGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.countGtX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(log^2 n * log U) -- how many edge weights on the path a..b are >= x; 0 when a == b (no edges)
    def edgePathCountGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.countGteX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(log^2 n * log U) -- how many edge weights on the path a..b are in [low, high]; 0 when a == b (no edges)
    def edgePathCountInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountInValRange", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.countInValRange
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], low, high)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, low, high)
        return res

    # O(log^2 n * log U) -- smallest of the edge weights on the path a..b that is >= x (None if none); None when a == b
    # (no edges)
    def edgePathSmallestGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSmallestGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.smallestGteX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v < res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r, x)
            if v is not None and (res is None or v < res):
                res = v
        return res

    # O(log^2 n * log U) -- smallest of the edge weights on the path a..b that is > x (None if none); None when a == b
    # (no edges)
    def edgePathSmallestGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSmallestGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.smallestGtX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v < res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r, x)
            if v is not None and (res is None or v < res):
                res = v
        return res

    # O(log^2 n * log U) -- largest of the edge weights on the path a..b that is <= x (None if none); None when a == b
    # (no edges)
    def edgePathLargestLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLargestLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.largestLteX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v > res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r, x)
            if v is not None and (res is None or v > res):
                res = v
        return res

    # O(log^2 n * log U) -- largest of the edge weights on the path a..b that is < x (None if none); None when a == b
    # (no edges)
    def edgePathLargestLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLargestLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.largestLtX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v > res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r, x)
            if v is not None and (res is None or v > res):
                res = v
        return res

    # O(log^2 n * log U) -- how many edge weights on the path a..b equal x; 0 when a == b (no edges)
    def edgePathCountOccurrences(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountOccurrences", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.countOccurrences
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(log n * log U) -- min edge weight in node's subtree; inf when node is a leaf (no edges)
    def edgeSubtreeMin(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMin", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return float("inf")
        return self.edgeSeg.rangeMin(l, r)

    # O(log n * log U) -- max edge weight in node's subtree; -inf when node is a leaf (no edges)
    def edgeSubtreeMax(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMax", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return float("-inf")
        return self.edgeSeg.rangeMax(l, r)

    # O(log n * log U) -- kth smallest of the edge weights in node's subtree (1-indexed: k = 1 is the min); needs at
    # least one edge (not node is a leaf), else IndexError
    def edgeSubtreeKthSmallest(self, node, k):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeKthSmallest", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            raise IndexError("edgeSubtreeKthSmallest: needs at least one edge in node's subtree")
        return self.edgeSeg.kthSmallest(l, r, k)

    # O(log n * log U) -- how many edge weights in node's subtree are < x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountLtX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.countLtX(l, r, x)

    # O(log n * log U) -- how many edge weights in node's subtree are <= x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountLteX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.countLteX(l, r, x)

    # O(log n * log U) -- how many edge weights in node's subtree are > x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountGtX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.countGtX(l, r, x)

    # O(log n * log U) -- how many edge weights in node's subtree are >= x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountGteX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.countGteX(l, r, x)

    # O(log n * log U) -- how many edge weights in node's subtree are in [low, high]; 0 when node is a leaf (no edges)
    def edgeSubtreeCountInValRange(self, node, low, high):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountInValRange", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.countInValRange(l, r, low, high)

    # O(log n * log U) -- smallest of the edge weights in node's subtree that is >= x (None if none); None when node is
    # a leaf (no edges)
    def edgeSubtreeSmallestGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeSmallestGteX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return None
        return self.edgeSeg.smallestGteX(l, r, x)

    # O(log n * log U) -- smallest of the edge weights in node's subtree that is > x (None if none); None when node is a
    # leaf (no edges)
    def edgeSubtreeSmallestGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeSmallestGtX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return None
        return self.edgeSeg.smallestGtX(l, r, x)

    # O(log n * log U) -- largest of the edge weights in node's subtree that is <= x (None if none); None when node is a
    # leaf (no edges)
    def edgeSubtreeLargestLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeLargestLteX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return None
        return self.edgeSeg.largestLteX(l, r, x)

    # O(log n * log U) -- largest of the edge weights in node's subtree that is < x (None if none); None when node is a
    # leaf (no edges)
    def edgeSubtreeLargestLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeLargestLtX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return None
        return self.edgeSeg.largestLtX(l, r, x)

    # O(log n * log U) -- how many edge weights in node's subtree equal x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountOccurrences(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountOccurrences", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.countOccurrences(l, r, x)

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
