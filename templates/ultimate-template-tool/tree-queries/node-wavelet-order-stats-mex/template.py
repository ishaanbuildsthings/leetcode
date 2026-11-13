# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/node-wavelet-order-stats-mex/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/wavelet-order-stats-mex/template.py
# @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeGet nodePathCountGtX nodePathCountGteX nodePathCountInValRange nodePathCountLtX nodePathCountLteX nodePathCountOccurrences nodePathLargestLtX nodePathLargestLteX nodePathMax nodePathMin nodePathSmallestGtX nodePathSmallestGteX nodeSubtreeCountGtX nodeSubtreeCountGteX nodeSubtreeCountInValRange nodeSubtreeCountLtX nodeSubtreeCountLteX nodeSubtreeCountOccurrences nodeSubtreeKthSmallest nodeSubtreeLargestLtX nodeSubtreeLargestLteX nodeSubtreeMax nodeSubtreeMex nodeSubtreeMin nodeSubtreeSmallestGtX nodeSubtreeSmallestGteX parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: wavelet
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
#   nodeGet: 1
#   nodePathCountGtX: log^2(N)
#   nodePathCountGteX: log^2(N)
#   nodePathCountInValRange: log^2(N)
#   nodePathCountLtX: log^2(N)
#   nodePathCountLteX: log^2(N)
#   nodePathCountOccurrences: log^2(N)
#   nodePathLargestLtX: log^2(N)
#   nodePathLargestLteX: log^2(N)
#   nodePathMax: log^2(N)
#   nodePathMin: log^2(N)
#   nodePathSmallestGtX: log^2(N)
#   nodePathSmallestGteX: log^2(N)
#   nodeSubtreeCountGtX: log(N)
#   nodeSubtreeCountGteX: log(N)
#   nodeSubtreeCountInValRange: log(N)
#   nodeSubtreeCountLtX: log(N)
#   nodeSubtreeCountLteX: log(N)
#   nodeSubtreeCountOccurrences: log(N)
#   nodeSubtreeKthSmallest: log(N)
#   nodeSubtreeLargestLtX: log(N)
#   nodeSubtreeLargestLteX: log(N)
#   nodeSubtreeMax: log(N)
#   nodeSubtreeMex: log(N)
#   nodeSubtreeMin: log(N)
#   nodeSubtreeSmallestGtX: log(N)
#   nodeSubtreeSmallestGteX: log(N)
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: log(N)
#   pathNodes: K+log(N)
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: log(N)
#   unweightedDistBetweenPaths: log(N)
#   unweightedDistToPath: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: zeros[1*N*log(N)] arr[1*N] srt[1*N] mexRoot[1*N] ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)]
#   tags: none
#   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value; rangeMex uses a persistent seg tree over the values 0..N+1 holding each value's last index

# Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
# 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x, lowVal,
# ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the ranks
# with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0, so a window
# [lo, hi) maps to [zeros[d][lo], zeros[d][hi]) among the 0s and to [nz + lo - zeros[d][lo], ...) among the 1s.
# rangeMex: a persistent seg tree over the values 0..N+1; version p holds, per value, its last index before p (-1 if
# none). The mex of a[l..r] is the first value whose last index in version r + 1 is < l.
from bisect import bisect_left, bisect_right
from itertools import accumulate, compress
from operator import ne


class WaveletMatrix:
    __slots__ = ('arr', 'n', 'srt', 'm', 'bits', 'zeros', 'mexRoot', 'ML', 'MR', 'MN')

    # O(N log N) -- arr: the initial array (a list), 0-indexed
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        order = sorted(range(self.n), key=arr.__getitem__)  # ranks by sorting, so no value is ever hashed
        s = [arr[i] for i in order]
        up = list(map(ne, s, s[1:]))  # up[k]: s[k + 1] starts a new distinct value
        self.srt = srt = s[:1] + list(compress(s[1:], up))
        self.m = m = len(srt)
        self.bits = bits = max(1, (m - 1).bit_length())
        cur = [0] * self.n
        for i, k in zip(order, accumulate(up, initial=0)):
            cur[i] = k
        self.zeros = []
        for d in range(bits - 1, -1, -1):
            self.zeros.append(list(accumulate((((v >> d) & 1) ^ 1 for v in cur), initial=0)))
            cur = [v for v in cur if not (v >> d) & 1] + [v for v in cur if (v >> d) & 1]
        self._buildMex()

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.arr[i]

    # O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self.countInValRange(l, r, x, x)

    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else IndexError
    def countInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countInValRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if lowVal > highVal:
            return 0
        return self._countBelow(l, r, bisect_right(self.srt, highVal)) - self._countBelow(l, r,
            bisect_left(self.srt, lowVal))

    # O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._countBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._countBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return r - l + 1 - self._countBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return r - l + 1 - self._countBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < n and 1 <= k <= r - l + 1, else
    # IndexError
    def kthSmallest(self, l, r, k):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"kthSmallest: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._kth(l, r, 1)

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._kth(l, r, r - l + 1)

    # O(logN) -- smallest value >= x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def smallestGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"smallestGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, bisect_left(self.srt, x))
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def smallestGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"smallestGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, bisect_right(self.srt, x))
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def largestLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"largestLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, bisect_right(self.srt, x))
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def largestLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"largestLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, bisect_left(self.srt, x))
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- smallest integer >= 0 that is not in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMex(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMex: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._mexFrom(l, r, 0)

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

    # ---- internals ----

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        lo, hi, rank, d = l, r + 1, 0, self.bits
        for z in self.zeros:
            d -= 1
            zl, zh = z[lo], z[hi]
            if k <= zh - zl:  # enough 0s at this bit: the answer has it 0
                lo, hi = zl, zh
            else:
                k -= zh - zl
                rank |= 1 << d
                lo, hi = z[-1] + lo - zl, z[-1] + hi - zh
        return self.srt[rank]

    # # of i in [l, r] whose rank is < x
    def _countBelow(self, l, r, x):
        if x <= 0:
            return 0
        if x >= self.m:
            return r - l + 1
        lo, hi, res, d = l, r + 1, 0, self.bits
        for z in self.zeros:
            d -= 1
            zl, zh = z[lo], z[hi]
            if (x >> d) & 1:  # everything with this bit 0 is below x; keep going among the 1s
                res += zh - zl
                lo, hi = z[-1] + lo - zl, z[-1] + hi - zh
            else:
                lo, hi = zl, zh
        return res

    # persistent seg tree over the values 0..n+1: version p holds, per value, its last index before p (-1: none)
    def _buildMex(self):
        n = self.n
        self.ML, self.MR, self.MN = [0], [0], [-1]  # node 0 = the empty tree (every last index -1)
        self.mexRoot = root = [0] * (n + 1)
        for i, v in enumerate(self.arr):
            root[i + 1] = self._mexSet(root[i], v, i) if 0 <= v <= n + 1 else root[i]

    # O(logN) -- copy of node with value v's last index set to i
    def _mexSet(self, node, v, i):
        ML, MR, MN = self.ML, self.MR, self.MN
        path = []
        nl, nh = 0, self.n + 1
        while nl != nh:
            mid = (nl + nh) >> 1
            if v <= mid:
                path.append((node, True))
                node, nh = ML[node], mid
            else:
                path.append((node, False))
                node, nl = MR[node], mid + 1
        cur = len(MN)
        ML.append(0), MR.append(0), MN.append(i)
        for old, left in reversed(path):
            lc, rc = (cur, MR[old]) if left else (ML[old], cur)
            cur = len(MN)
            ML.append(lc), MR.append(rc), MN.append(min(MN[lc], MN[rc]))
        return cur

    # O(logN) -- smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    def _mexFrom(self, l, r, s):
        ML, MR, MN = self.ML, self.MR, self.MN
        stack = [(self.mexRoot[r + 1], 0, self.n + 1)]
        while stack:
            t, nl, nh = stack.pop()
            if nh < s or MN[t] >= l:  # nothing allowed here, or every value here is in a[l..r]
                continue
            if not t:  # no value here was ever seen
                return max(nl, s)
            if nl == nh:
                return nl
            mid = (nl + nh) >> 1
            stack.append((MR[t], mid + 1, nh))
            stack.append((ML[t], nl, mid))
        return self.n + 2  # (unreachable: the n + 2 values 0..n+1 can't all be in a[l..r])


from bisect import bisect_left


# tree = Tree(edges, root, vals)
#
# edges: the tree's n - 1 edges. Whether nodes are 0..n-1 or 1..n is detected automatically from the edge list
#        (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b), ...]        e.g. [(0, 1), (1, 2)]
#   [(a, b, w), ...]     also accepted: the weights are ignored here
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
#
#   Tree([(0, 1), (1, 2)], 0, [10, 20, 30])       # nodes 0..2, rooted at 0
#   Tree([(1, 2), (2, 3)], 1, [0, 10, 20, 30])    # nodes 1..3, rooted at 1
#
# Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree raises
# IndexError. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). The values sit in the range structure above
# (WaveletMatrix) in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per chain it
# crosses.
class Tree:
    # O(n * log n) -- builds the layout and the range structure; raises ValueError when the edges are not one tree on
    # nodes 0..n-1 or 1..n, or vals has the wrong length
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
        self.seg = WaveletMatrix([vals[v] for v in order])  # the values, in position order

    # O(1) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.seg.pointGet(self.pos[node])

    # O(log^2 n) -- min node value on the path a..b
    def nodePathMin(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMin", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeMin
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
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeMax
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

    # O(log^2 n) -- how many node values on the path a..b are < x
    def nodePathCountLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countLtX
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

    # O(log^2 n) -- how many node values on the path a..b are <= x
    def nodePathCountLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countLteX
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

    # O(log^2 n) -- how many node values on the path a..b are > x
    def nodePathCountGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countGtX
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

    # O(log^2 n) -- how many node values on the path a..b are >= x
    def nodePathCountGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countGteX
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

    # O(log^2 n) -- how many node values on the path a..b are in [low, high]
    def nodePathCountInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountInValRange", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countInValRange
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

    # O(log^2 n) -- smallest of the node values on the path a..b that is >= x (None if none)
    def nodePathSmallestGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSmallestGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.smallestGteX
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

    # O(log^2 n) -- smallest of the node values on the path a..b that is > x (None if none)
    def nodePathSmallestGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSmallestGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.smallestGtX
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

    # O(log^2 n) -- largest of the node values on the path a..b that is <= x (None if none)
    def nodePathLargestLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLargestLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.largestLteX
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

    # O(log^2 n) -- largest of the node values on the path a..b that is < x (None if none)
    def nodePathLargestLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLargestLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.largestLtX
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

    # O(log^2 n) -- how many node values on the path a..b equal x
    def nodePathCountOccurrences(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountOccurrences", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countOccurrences
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

    # O(log n) -- min node value in node's subtree
    def nodeSubtreeMin(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMin", node)
        l = self.pos[node]
        return self.seg.rangeMin(l, l + self.sz[node] - 1)

    # O(log n) -- max node value in node's subtree
    def nodeSubtreeMax(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMax", node)
        l = self.pos[node]
        return self.seg.rangeMax(l, l + self.sz[node] - 1)

    # O(log n) -- kth smallest of the node values in node's subtree (1-indexed: k = 1 is the min)
    def nodeSubtreeKthSmallest(self, node, k):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeKthSmallest", node)
        l = self.pos[node]
        return self.seg.kthSmallest(l, l + self.sz[node] - 1, k)

    # O(log n) -- how many node values in node's subtree are < x
    def nodeSubtreeCountLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountLtX", node)
        l = self.pos[node]
        return self.seg.countLtX(l, l + self.sz[node] - 1, x)

    # O(log n) -- how many node values in node's subtree are <= x
    def nodeSubtreeCountLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountLteX", node)
        l = self.pos[node]
        return self.seg.countLteX(l, l + self.sz[node] - 1, x)

    # O(log n) -- how many node values in node's subtree are > x
    def nodeSubtreeCountGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountGtX", node)
        l = self.pos[node]
        return self.seg.countGtX(l, l + self.sz[node] - 1, x)

    # O(log n) -- how many node values in node's subtree are >= x
    def nodeSubtreeCountGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountGteX", node)
        l = self.pos[node]
        return self.seg.countGteX(l, l + self.sz[node] - 1, x)

    # O(log n) -- how many node values in node's subtree are in [low, high]
    def nodeSubtreeCountInValRange(self, node, low, high):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountInValRange", node)
        l = self.pos[node]
        return self.seg.countInValRange(l, l + self.sz[node] - 1, low, high)

    # O(log n) -- smallest of the node values in node's subtree that is >= x (None if none)
    def nodeSubtreeSmallestGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSmallestGteX", node)
        l = self.pos[node]
        return self.seg.smallestGteX(l, l + self.sz[node] - 1, x)

    # O(log n) -- smallest of the node values in node's subtree that is > x (None if none)
    def nodeSubtreeSmallestGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSmallestGtX", node)
        l = self.pos[node]
        return self.seg.smallestGtX(l, l + self.sz[node] - 1, x)

    # O(log n) -- largest of the node values in node's subtree that is <= x (None if none)
    def nodeSubtreeLargestLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeLargestLteX", node)
        l = self.pos[node]
        return self.seg.largestLteX(l, l + self.sz[node] - 1, x)

    # O(log n) -- largest of the node values in node's subtree that is < x (None if none)
    def nodeSubtreeLargestLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeLargestLtX", node)
        l = self.pos[node]
        return self.seg.largestLtX(l, l + self.sz[node] - 1, x)

    # O(log n) -- how many node values in node's subtree equal x
    def nodeSubtreeCountOccurrences(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountOccurrences", node)
        l = self.pos[node]
        return self.seg.countOccurrences(l, l + self.sz[node] - 1, x)

    # O(log n) -- smallest integer >= 0 missing from the node values in node's subtree
    def nodeSubtreeMex(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMex", node)
        l = self.pos[node]
        return self.seg.rangeMex(l, l + self.sz[node] - 1)

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
