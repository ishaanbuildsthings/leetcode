# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeSum-rangeXorQuery-rightmostSuffixSumGtX-rightmostSuffixSumGteX/sparse.py
# @operations: maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeSum rangeXorQuery rightmostSuffixSumGtX rightmostSuffixSumGteX
# @data-structure-type: lazy-seg-tree
# @complexities:
#   maxSuffixSum: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeAssign: log(U)
#   rangeSum: log(U)
#   rangeXorQuery: log(U)
#   rightmostSuffixSumGtX: log(U)
#   rightmostSuffixSumGteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[4*log(U)] suf[4*log(U)] xr[4*log(U)]
#   tags: asg[4*log(U)] hasAsg[4*log(U)]
#   other: children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

# Lazy segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
# position starting at 0; range updates (rangeAssign) and range queries in O(logU), U = hi - lo + 1; each node keeps
# its sum, its best suffix sum, its xor over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing
# qualifies. The root covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so a node of level
# s covers 2^s positions; children are created on demand as blocks of zeros, right before anything descends past a
# node, and a node's pending tags ("applied here, not yet to my children") go down as it is passed.

class SparseLazySegTree:
    __slots__ = ('first', 'last', 'D', 'L', 'R', 'sm', 'suf', 'xr', 'asg', 'hasAsg')


    # O(1) -- all zeros over [lo, hi]; any range of integers works (lo <= hi)
    def __init__(self, lo, hi):
        self.first, self.last = lo, hi  # (the index range: lo / hi are the clamp tags' names)
        self.D = (hi - lo).bit_length()  # the root's level: 2^D >= hi - lo + 1
        self.L, self.R = [0], [0]  # node 0: none (node 1 is the root)
        self.sm = [0]
        self.suf = [0]
        self.xr = [0]
        self.asg = [0]
        self.hasAsg = [0]
        self._newZero(self.D)

    # O(logN) -- max of a[i] + ... + a[r] over i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def maxSuffixSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"maxSuffixSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, suf = self.sm, self.suf
        ns = self._nodes(l, r)
        t = ns[-1][0]
        res, acc = suf[t], sm[t]
        for t, _ in reversed(ns[:-1]):
            if acc + suf[t] > res:
                res = acc + suf[t]
            acc += sm[t]
        return res

    # O(logU) -- a[i] += v; needs lo <= i <= hi, else IndexError
    def pointAdd(self, i, v):
        if not self.first <= i <= self.last:
            raise IndexError(f"pointAdd: needs lo <= i <= hi, got i = {i}")
        x, path = self._leafOf(i)
        self._setLeaf(x, self._leaf(x) + v)
        self._up(path)

    # O(logU) -- a[i] = v; needs lo <= i <= hi, else IndexError
    def pointAssign(self, i, v):
        if not self.first <= i <= self.last:
            raise IndexError(f"pointAssign: needs lo <= i <= hi, got i = {i}")
        x, path = self._leafOf(i)
        self._setLeaf(x, v)
        self._up(path)

    # O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else IndexError
    def pointChmax(self, i, v):
        if not self.first <= i <= self.last:
            raise IndexError(f"pointChmax: needs lo <= i <= hi, got i = {i}")
        x, path = self._leafOf(i)
        self._setLeaf(x, max(self._leaf(x), v))
        self._up(path)

    # O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else IndexError
    def pointChmin(self, i, v):
        if not self.first <= i <= self.last:
            raise IndexError(f"pointChmin: needs lo <= i <= hi, got i = {i}")
        x, path = self._leafOf(i)
        self._setLeaf(x, min(self._leaf(x), v))
        self._up(path)

    # O(logU) -- a[i]; needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.first <= i <= self.last:
            raise IndexError(f"pointGet: needs lo <= i <= hi, got i = {i}")
        return self._leaf(self._leafOf(i)[0])

    # O(logU) -- a[i] = v for i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def rangeAssign(self, l, r, v):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeAssign: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._applyAssign(t, s, v))

    # O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, res = self.sm, 0
        for t, _ in self._nodes(l, r):
            res += sm[t]
        return res

    # O(logU) -- a[l] ^ ... ^ a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeXorQuery(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeXorQuery: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        xr, res = self.xr, 0
        for t, _ in self._nodes(l, r):
            res ^= xr[t]
        return res

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] > x, or lo - 1 (a walk pruned by best suffix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostSuffixSumGtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostSuffixSumGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.suf, self.L, self.R
        acc = 0
        for t, s, tl in reversed(self._cover(l, r)):
            if acc + P[t] > x:
                while s:
                    self._kids(t, s)
                    self._push(t, s)
                    s -= 1
                    if acc + P[R[t]] > x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        acc += sm[R[t]]
                        t = L[t]
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] >= x, or lo - 1 (a walk pruned by best suffix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostSuffixSumGteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostSuffixSumGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.suf, self.L, self.R
        acc = 0
        for t, s, tl in reversed(self._cover(l, r)):
            if acc + P[t] >= x:
                while s:
                    self._kids(t, s)
                    self._push(t, s)
                    s -= 1
                    if acc + P[R[t]] >= x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        acc += sm[R[t]]
                        t = L[t]
                return tl
            acc += sm[t]
        return self.first - 1

    # ---- internals ----

    def _newZero(self, s):  # a new node: a block of 2^s zeros
        self.L.append(0)
        self.R.append(0)
        self.sm.append(0)
        self.suf.append(0)
        self.xr.append(0)
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
        self.sm[p] = v
        self.suf[p] = v
        self.xr[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children
        a, b = self.L[x], self.R[x]
        sm = self.sm
        self.suf[x] = max(self.suf[b], sm[b] + self.suf[a])
        sm[x] = sm[a] + sm[b]
        self.xr[x] = self.xr[a] ^ self.xr[b]

    def _setAssign(self, x, s, v):  # every value under node x becomes v
        k = 1 << s
        self.sm[x] = v * k
        self.suf[x] = v * k if v > 0 else v
        self.xr[x] = v if k & 1 else 0

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
