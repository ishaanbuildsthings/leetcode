# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/seg-tree-sum-min-max-pre-suf-best-npre-nsuf/sparse.py
# @operations: leftmostGtX leftmostGteX leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX leftmostPrefixSumLtX leftmostPrefixSumLteX maxPrefixSum maxSubarraySum maxSuffixSum minPrefixSum minSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX rightmostSuffixSumLtX rightmostSuffixSumLteX
# @data-structure-type: seg-tree
# @complexities:
#   leftmostGtX: log(U)
#   leftmostGteX: log(U)
#   leftmostLtX: log(U)
#   leftmostLteX: log(U)
#   leftmostPrefixSumGtX: log(U)
#   leftmostPrefixSumGteX: log(U)
#   leftmostPrefixSumLtX: log(U)
#   leftmostPrefixSumLteX: log(U)
#   maxPrefixSum: log(U)
#   maxSubarraySum: log(U)
#   maxSuffixSum: log(U)
#   minPrefixSum: log(U)
#   minSuffixSum: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeMax: log(U)
#   rangeMin: log(U)
#   rangeSum: log(U)
#   rightmostGtX: log(U)
#   rightmostGteX: log(U)
#   rightmostLtX: log(U)
#   rightmostLteX: log(U)
#   rightmostSuffixSumGtX: log(U)
#   rightmostSuffixSumGteX: log(U)
#   rightmostSuffixSumLtX: log(U)
#   rightmostSuffixSumLteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[4*log(U)] mn[4*log(U)] mx[4*log(U)] pre[4*log(U)] suf[4*log(U)] best[4*log(U)] npre[4*log(U)] nsuf[4*log(U)]
#   tags: none
#   other: children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

# Segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
# position starting at 0; point updates and range queries in O(logU), U = hi - lo + 1; each node keeps its sum, its
# min, its max, its best prefix sum, its best suffix sum, its best subarray sum, its min prefix sum, its min suffix
# sum over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U
# positions from lo (the ones past hi are zeros nobody reads), so a node of level s covers 2^s positions; children are
# created on demand as blocks of zeros, right before anything descends past a node.

INF, NEG = float("inf"), float("-inf")


class SparseSegTree:
    __slots__ = ('first', 'last', 'D', 'L', 'R', 'sm', 'mn', 'mx', 'pre', 'suf', 'best', 'npre', 'nsuf')


    # O(1) -- all zeros over [lo, hi]; any range of integers works (lo <= hi)
    def __init__(self, lo, hi):
        self.first, self.last = lo, hi  # (the index range: lo / hi are the clamp tags' names)
        self.D = (hi - lo).bit_length()  # the root's level: 2^D >= hi - lo + 1
        self.L, self.R = [0], [0]  # node 0: none (node 1 is the root)
        self.sm = [0]
        self.mn = [0]
        self.mx = [0]
        self.pre = [0]
        self.suf = [0]
        self.best = [0]
        self.npre = [0]
        self.nsuf = [0]
        self._newZero(self.D)

    # O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostGtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[L[t]] > x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

    # O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostGteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] >= x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[L[t]] >= x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

    # O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostLtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mn, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] < x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[L[t]] < x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

    # O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostLteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mn, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] <= x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[L[t]] <= x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1 (a walk pruned by best prefix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostPrefixSumGtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostPrefixSumGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.pre, self.L, self.R
        acc = 0
        for t, s, tl in self._cover(l, r):
            if acc + P[t] > x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[L[t]] > x:
                        t = L[t]
                    else:
                        acc += sm[L[t]]
                        t, tl = R[t], tl + (1 << s)
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1 (a walk pruned by best prefix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostPrefixSumGteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostPrefixSumGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.pre, self.L, self.R
        acc = 0
        for t, s, tl in self._cover(l, r):
            if acc + P[t] >= x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[L[t]] >= x:
                        t = L[t]
                    else:
                        acc += sm[L[t]]
                        t, tl = R[t], tl + (1 << s)
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] < x, or lo - 1 (a walk pruned by min prefix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostPrefixSumLtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostPrefixSumLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.npre, self.L, self.R
        acc = 0
        for t, s, tl in self._cover(l, r):
            if acc + P[t] < x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[L[t]] < x:
                        t = L[t]
                    else:
                        acc += sm[L[t]]
                        t, tl = R[t], tl + (1 << s)
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] <= x, or lo - 1 (a walk pruned by min prefix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostPrefixSumLteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostPrefixSumLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.npre, self.L, self.R
        acc = 0
        for t, s, tl in self._cover(l, r):
            if acc + P[t] <= x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[L[t]] <= x:
                        t = L[t]
                    else:
                        acc += sm[L[t]]
                        t, tl = R[t], tl + (1 << s)
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logN) -- max of a[l] + ... + a[i] over i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def maxPrefixSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"maxPrefixSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, pre = self.sm, self.pre
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, acc = pre[t], sm[t]
        for t, _ in ns[1:]:
            if acc + pre[t] > res:
                res = acc + pre[t]
            acc += sm[t]
        return res

    # O(logN) -- max sum of a non-empty contiguous subarray of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def maxSubarraySum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"maxSubarraySum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, pre, suf, best = self.sm, self.pre, self.suf, self.best
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, q = best[t], suf[t]  # (q: the best sum ending at the right edge so far)
        for t, _ in ns[1:]:
            res = max(res, best[t], q + pre[t])
            q = max(suf[t], sm[t] + q)
        return res

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

    # O(logN) -- min of a[l] + ... + a[i] over i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def minPrefixSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"minPrefixSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, npre = self.sm, self.npre
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, acc = npre[t], sm[t]
        for t, _ in ns[1:]:
            if acc + npre[t] < res:
                res = acc + npre[t]
            acc += sm[t]
        return res

    # O(logN) -- min of a[i] + ... + a[r] over i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def minSuffixSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"minSuffixSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, nsuf = self.sm, self.nsuf
        ns = self._nodes(l, r)
        t = ns[-1][0]
        res, acc = nsuf[t], sm[t]
        for t, _ in reversed(ns[:-1]):
            if acc + nsuf[t] < res:
                res = acc + nsuf[t]
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

    # O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMax(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeMax: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        mx, res = self.mx, NEG
        for t, _ in self._nodes(l, r):
            if mx[t] > res:
                res = mx[t]
        return res

    # O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMin(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeMin: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        mn, res = self.mn, INF
        for t, _ in self._nodes(l, r):
            if mn[t] < res:
                res = mn[t]
        return res

    # O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, res = self.sm, 0
        for t, _ in self._nodes(l, r):
            res += sm[t]
        return res

    # O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostGtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[R[t]] > x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]
                return tl
        return self.first - 1

    # O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostGteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] >= x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[R[t]] >= x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]
                return tl
        return self.first - 1

    # O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostLtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mn, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] < x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[R[t]] < x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]
                return tl
        return self.first - 1

    # O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostLteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mn, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] <= x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[R[t]] <= x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]
                return tl
        return self.first - 1

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
                    s -= 1
                    if acc + P[R[t]] >= x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        acc += sm[R[t]]
                        t = L[t]
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] < x, or lo - 1 (a walk pruned by min suffix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostSuffixSumLtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostSuffixSumLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.nsuf, self.L, self.R
        acc = 0
        for t, s, tl in reversed(self._cover(l, r)):
            if acc + P[t] < x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[R[t]] < x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        acc += sm[R[t]]
                        t = L[t]
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] <= x, or lo - 1 (a walk pruned by min suffix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostSuffixSumLteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostSuffixSumLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.nsuf, self.L, self.R
        acc = 0
        for t, s, tl in reversed(self._cover(l, r)):
            if acc + P[t] <= x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[R[t]] <= x:
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
        self.mn.append(0)
        self.mx.append(0)
        self.pre.append(0)
        self.suf.append(0)
        self.best.append(0)
        self.npre.append(0)
        self.nsuf.append(0)
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
        m = tl + (1 << (s - 1))
        if l < m:
            self._collect(self.L[x], s - 1, tl, l, r, out)
        if r >= m:
            self._collect(self.R[x], s - 1, m, l, r, out)

    def _nodes(self, l, r):  # the covering nodes left to right, each with its level
        return [(x, s) for x, s, _ in self._cover(l, r)]

    def _leafOf(self, i):  # (the leaf holding a[i], the nodes above it top-down), every tag on the way pushed
        x, s, tl, path = 1, self.D, self.first, []
        while s:
            self._kids(x, s)
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
            self._pull(path[k])

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.mn[p] = v
        self.mx[p] = v
        self.pre[p] = v
        self.suf[p] = v
        self.best[p] = v
        self.npre[p] = v
        self.nsuf[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x):  # recompute node x from its children
        a, b = self.L[x], self.R[x]
        sm = self.sm
        self.pre[x] = max(self.pre[a], sm[a] + self.pre[b])
        self.suf[x] = max(self.suf[b], sm[b] + self.suf[a])
        self.best[x] = max(self.best[a], self.best[b], self.suf[a] + self.pre[b])
        self.npre[x] = min(self.npre[a], sm[a] + self.npre[b])
        self.nsuf[x] = min(self.nsuf[b], sm[b] + self.nsuf[a])
        sm[x] = sm[a] + sm[b]
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w
