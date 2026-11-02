# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeGcd-rangeOrQuery/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd rangeOrQuery
# @data-structure-type: seg-tree
# @complexities:
#   getAll: N
#   pointAdd: log(N)*log(U) ?
#   pointAssign: log(N)*log(U) ?
#   pointChmax: log(N)*log(U) ?
#   pointChmin: log(N)*log(U) ?
#   pointGet: log(N)
#   rangeGcd: log(N)+log(U) ?
#   rangeOrQuery: log(N)
#   build: N*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: orr[2*N] g[2*N]
#   tags: none
#   other: none
#   note: leaves [n, 2n) hold each value's own aggregates

# Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
# its OR, its gcd over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing
# qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its level);
# an update rewrites a leaf, then its ancestors.
from math import gcd


class SegTree:
    __slots__ = ('n', 'h', 'orr', 'g')


    # O(N log U) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.orr = [0] * n + list(arr)
        self.g = [0] * n + list(arr)
        for x in range(n - 1, 0, -1):
            self._pull(x)

    # O(N) -- the whole array
    def getAll(self):
        return self.orr[self.n:]

    # O(logN * logU) -- a[i] += v
    def pointAdd(self, i, v):
        p = i + self.n
        self._setLeaf(p, self._leaf(p) + v)
        self._rebuild(p)

    # O(logN * logU) -- a[i] = v
    def pointAssign(self, i, v):
        p = i + self.n
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN * logU) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        p = i + self.n
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN * logU) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        p = i + self.n
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        return self._leaf(p)

    # O(logN + logU) -- gcd of |a[l]|, ..., |a[r]|
    def rangeGcd(self, l, r):
        n, g = self.n, self.g
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res = gcd(res, g[lo])
                lo += 1
            if hi & 1:
                hi -= 1
                res = gcd(res, g[hi])
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r):
        n, orr = self.n, self.orr
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res |= orr[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res |= orr[hi]
            lo >>= 1
            hi >>= 1
        return res

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.orr[p] = v
        self.g[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.orr[p]

    def _pull(self, x):  # recompute node x from its children
        a, b = 2 * x, 2 * x + 1
        self.orr[x] = self.orr[a] | self.orr[b]
        self.g[x] = gcd(self.g[a], self.g[b])

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
