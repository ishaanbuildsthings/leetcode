# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmax-rangeChmin-rangeMin-rightmostLtX-rightmostLteX/template.py
# @operations: getAll leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeChmin rangeMin rightmostLtX rightmostLteX
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAssign: log(N)
#   rangeChmax: log(N)
#   rangeChmin: log(N)
#   rangeMin: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: mn[2*N]
#   tags: hi[1*N] lo[1*N]
#   other: none
#   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

# Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAssign, rangeChmax, rangeChmin) and
# range queries in O(logN); each node keeps its min over its range. All indices 0-based, ranges inclusive [l, r];
# searches return -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree
# of 2^s leaves (s = its level), and every internal node holds its pending tags ("applied here, not yet to my
# children"): an update pushes the tags on its two boundary leaf paths, tags the covering nodes, then rebuilds both
# paths, each node redoing its own pending tag.

INF, NEG = float("inf"), float("-inf")


class LazySegTree:
    __slots__ = ('n', 'h', 'mn', 'hi', 'lo')


    # O(N) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.mn = [0] * n + list(arr)
        self.hi = [INF] * n
        self.lo = [NEG] * n
        for x in range(n - 1, 0, -1):
            self._pull(x)

    # O(N) -- the whole array, every pending tag pushed down on the way
    def getAll(self):
        n = self.n
        for x in range(1, n):  # (parents before children)
            self._push(x)
        return [self._leaf(p) for p in range(n, 2 * n)]

    # O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    def leftmostLtX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] < x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t)
                    t = 2 * t if F[2 * t] < x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min)
    def leftmostLteX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] <= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t)
                    t = 2 * t if F[2 * t] <= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- a[i] += v
    def pointAdd(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, self._leaf(p) + v)
        self._rebuild(p)

    # O(logN) -- a[i] = v
    def pointAssign(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        self._pushPath(p)
        return self._leaf(p)

    # O(logN) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi = l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                self._applyClamp(lo, v, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._applyClamp(hi, v, v)
            lo >>= 1
            hi >>= 1
        self._rebuild(l + n)
        self._rebuild(r + n)

    # O(logN) -- a[i] = max(a[i], v) for i in [l, r]
    def rangeChmax(self, l, r, v):
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi = l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                self._applyClamp(lo, INF, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._applyClamp(hi, INF, v)
            lo >>= 1
            hi >>= 1
        self._rebuild(l + n)
        self._rebuild(r + n)

    # O(logN) -- a[i] = min(a[i], v) for i in [l, r]
    def rangeChmin(self, l, r, v):
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi = l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                self._applyClamp(lo, v, NEG)
                lo += 1
            if hi & 1:
                hi -= 1
                self._applyClamp(hi, v, NEG)
            lo >>= 1
            hi >>= 1
        self._rebuild(l + n)
        self._rebuild(r + n)

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        n, mn = self.n, self.mn
        self._pushPath(l + n)
        self._pushPath(r + n)
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

    # O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    def rightmostLtX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] < x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t)
                    t = 2 * t + 1 if F[2 * t + 1] < x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min)
    def rightmostLteX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] <= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t)
                    t = 2 * t + 1 if F[2 * t + 1] <= x else 2 * t
                return t - n
        return -1

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.mn[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.mn[p]

    def _pull(self, x):  # recompute node x from its children, then redo its own pending tags
        a, b = 2 * x, 2 * x + 1
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        if self.hi[x] != INF or self.lo[x] != NEG:
            self._setClamp(x, self.hi[x], self.lo[x])

    def _rebuild(self, p):  # recompute every ancestor of leaf p
        while p > 1:
            p >>= 1
            self._pull(p)

    def _nodes(self, l, r):  # the O(logN) nodes covering a[l..r], left to right, each with its level
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
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

    def _setClamp(self, x, H, Lo):  # every value v under node x becomes min(H, max(Lo, v))
        self.mn[x] = min(H, max(Lo, self.mn[x]))

    def _applyClamp(self, x, H, Lo):
        self._setClamp(x, H, Lo)
        if x < self.n:
            h = min(H, max(Lo, self.hi[x]))
            self.lo[x] = min(max(Lo, self.lo[x]), h)
            self.hi[x] = h

    def _push(self, x):  # hand node x's pending tags to its children
        a, b = 2 * x, 2 * x + 1
        if self.hi[x] != INF or self.lo[x] != NEG:
            self._applyClamp(a, self.hi[x], self.lo[x])
            self._applyClamp(b, self.hi[x], self.lo[x])
            self.hi[x], self.lo[x] = INF, NEG

    def _pushPath(self, p):  # hand down every pending tag on the path from the root to leaf p
        for s in range(self.h, 0, -1):
            self._push(p >> s)
