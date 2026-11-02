# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeGcd-rangeXorQuery/sparse.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeGcd rangeXorQuery
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(U)*log(U) ?
#   pointAssign: log(U)*log(U) ?
#   pointChmax: log(U)*log(U) ?
#   pointChmin: log(U)*log(U) ?
#   pointGet: log(U)
#   rangeAssign: log(U)*log(U) ?
#   rangeGcd: log(U) ?
#   rangeXorQuery: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: xr[4*log(U)] g[4*log(U)]
#   tags: asg[4*log(U)] hasAsg[4*log(U)]
#   other: children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

# Lazy segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
# position starting at 0; range updates (rangeAssign) and range queries in O(logU), U = hi - lo + 1; each node keeps
# its xor, its gcd over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root
# covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so a node of level s covers 2^s
# positions; children are created on demand as blocks of zeros, right before anything descends past a node, and a
# node's pending tags ("applied here, not yet to my children") go down as it is passed.
from math import gcd


class SparseLazySegTree:
    __slots__ = ('first', 'last', 'D', 'L', 'R', 'xr', 'g', 'asg', 'hasAsg')


    # O(1) -- all zeros over [lo, hi]; any range of integers works (lo <= hi)
    def __init__(self, lo, hi):
        self.first, self.last = lo, hi  # (the index range: lo / hi are the clamp tags' names)
        self.D = (hi - lo).bit_length()  # the root's level: 2^D >= hi - lo + 1
        self.L, self.R = [0], [0]  # node 0: none (node 1 is the root)
        self.xr = [0]
        self.g = [0]
        self.asg = [0]
        self.hasAsg = [0]
        self._newZero(self.D)

    # O(logU * logU) -- a[i] += v
    def pointAdd(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, self._leaf(x) + v)
        self._up(path)

    # O(logU * logU) -- a[i] = v
    def pointAssign(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, v)
        self._up(path)

    # O(logU * logU) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, max(self._leaf(x), v))
        self._up(path)

    # O(logU * logU) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, min(self._leaf(x), v))
        self._up(path)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._leaf(self._leafOf(i)[0])

    # O(logU * logU) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._applyAssign(t, s, v))

    # O(logU + logU) -- gcd of |a[l]|, ..., |a[r]|
    def rangeGcd(self, l, r):
        g, res = self.g, 0
        for t, _ in self._nodes(l, r):
            res = gcd(res, g[t])
        return res

    # O(logU) -- a[l] ^ ... ^ a[r]
    def rangeXorQuery(self, l, r):
        xr, res = self.xr, 0
        for t, _ in self._nodes(l, r):
            res ^= xr[t]
        return res

    # ---- internals ----

    def _newZero(self, s):  # a new node: a block of 2^s zeros
        self.L.append(0)
        self.R.append(0)
        self.xr.append(0)
        self.g.append(0)
        self.asg.append(0)
        self.hasAsg.append(0)
        return len(self.L) - 1

    def _kids(self, x, s):  # create node x's children (blocks of zeros) if it has none yet
        if not self.L[x]:
            a = self._newZero(s - 1)
            self.L[x], self.R[x] = a, self._newZero(s - 1)

    def _cover(self, l, r):  # the nodes covering a[l..r], left to right, as (node, level, first index)
        out = []
        self._collect(1, self.D, self.first, l, r, out)
        return out

    def _collect(self, x, s, tl, l, r, out):
        if l <= tl and tl + (1 << s) - 1 <= r:
            out.append((x, s, tl))
            return
        self._kids(x, s)
        self._push(x, s)
        m = tl + (1 << (s - 1))
        if l < m:
            self._collect(self.L[x], s - 1, tl, l, r, out)
        if r >= m:
            self._collect(self.R[x], s - 1, m, l, r, out)

    def _nodes(self, l, r):  # the covering nodes left to right, each with its level
        return [(x, s) for x, s, _ in self._cover(l, r)]

    def _update(self, x, s, tl, l, r, f):  # f(node, level, first index) on every node covering a[l..r], then pull up
        if l <= tl and tl + (1 << s) - 1 <= r:
            f(x, s, tl)
            return
        self._kids(x, s)
        self._push(x, s)
        m = tl + (1 << (s - 1))
        if l < m:
            self._update(self.L[x], s - 1, tl, l, r, f)
        if r >= m:
            self._update(self.R[x], s - 1, m, l, r, f)
        self._pull(x, s)

    def _leafOf(self, i):  # (the leaf holding a[i], the nodes above it top-down), every tag on the way pushed
        x, s, tl, path = 1, self.D, self.first, []
        while s:
            self._kids(x, s)
            self._push(x, s)
            path.append(x)
            s -= 1
            if i >= tl + (1 << s):
                tl += 1 << s
                x = self.R[x]
            else:
                x = self.L[x]
        return x, path

    def _up(self, path):  # recompute the nodes of path, deepest first (path[k] has level D - k)
        for k in range(len(path) - 1, -1, -1):
            self._pull(path[k], self.D - k)

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.xr[p] = v
        self.g[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.xr[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children
        a, b = self.L[x], self.R[x]
        self.xr[x] = self.xr[a] ^ self.xr[b]
        self.g[x] = gcd(self.g[a], self.g[b])

    def _setAssign(self, x, s, v):  # every value under node x becomes v
        k = 1 << s
        self.xr[x] = v if k & 1 else 0
        self.g[x] = v  # (read through a gcd: |v|)

    def _applyAssign(self, x, s, v):
        self._setAssign(x, s, v)
        self.asg[x], self.hasAsg[x] = v, 1

    def _push(self, x, s):  # hand node x's pending tags to its children
        a, b = self.L[x], self.R[x]
        c = s - 1  # (their level)
        if self.hasAsg[x]:
            v = self.asg[x]
            self._applyAssign(a, c, v)
            self._applyAssign(b, c, v)
            self.hasAsg[x] = 0
