# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxPrefixSum-maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeSum/template.py
# @operations: getAll maxPrefixSum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeSum
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   maxPrefixSum: log(N)
#   maxSuffixSum: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAssign: log(N)
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: pow2-iterative
#   node: sm[4*N] pre[4*N] suf[4*N]
#   tags: asg[2*N] hasAsg[2*N]
#   other: none
#   note: tags live on the internal nodes only

# Range max prefix / max suffix sum, plus range sum, with RANGE ASSIGN and point updates. All indices 0-based, ranges inclusive
# [l, r]. The maxima are over NON-EMPTY pieces; when the empty piece is allowed (answer >= 0), take max(0, ...).
# A node assigned v over len slots is fully known: sum = v * len, and its best prefix / suffix is v * len if v > 0,
# else just v (one element). So assign is an ordinary lazy tag. Iterative lazy tree over a power-of-two layout;
# queries fold a left and a right accumulator (not commutative).


class MaxPrefixSuffixAssignTree:
    __slots__ = ("n", "size", "H", "sm", "pre", "suf", "asg", "hasAsg")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        size, H = 1, 0
        while size < max(n, 1):
            size <<= 1
            H += 1
        self.size, self.H = size, H
        self.sm = [0] * (2 * size)
        self.pre = [0] * (2 * size)
        self.suf = [0] * (2 * size)
        for i, v in enumerate(arr):
            p = size + i
            self.sm[p] = self.pre[p] = self.suf[p] = v
        for x in range(size - 1, 0, -1):
            self._pull(x)
        self.asg = [0] * size  # tags live on internal nodes only
        self.hasAsg = [False] * size

    @staticmethod
    def _merge(a, b):
        return (a[0] + b[0], max(a[1], a[0] + b[1]), max(b[2], b[0] + a[2]))

    def _node(self, x):
        return self.sm[x], self.pre[x], self.suf[x]

    def _pull(self, x):
        self.sm[x], self.pre[x], self.suf[x] = self._merge(self._node(2 * x), self._node(2 * x + 1))

    # node x (covering `length` slots) becomes `length` copies of v
    def _setAll(self, x, length, v):
        s = v * length
        b = s if v > 0 else v
        self.sm[x] = s
        self.pre[x] = self.suf[x] = b
        if x < self.size:
            self.hasAsg[x] = True
            self.asg[x] = v

    def _push(self, x, childLen):
        if self.hasAsg[x]:
            v = self.asg[x]
            self._setAll(2 * x, childLen, v)
            self._setAll(2 * x + 1, childLen, v)
            self.hasAsg[x] = False

    def _pushToRoot(self, p):
        for s in range(self.H, 0, -1):
            self._push(p >> s, 1 << (s - 1))

    # a node assigned during this update keeps its own tag's value
    def _recomputeToRoot(self, p):
        p >>= 1
        length = 2
        while p:
            if self.hasAsg[p]:
                self._setAll(p, length, self.asg[p])
            else:
                self._pull(p)
            p >>= 1
            length <<= 1

    # O(logN) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        if l > r:
            return
        l0, r0 = l + self.size, r + self.size
        self._pushToRoot(l0)
        self._pushToRoot(r0)
        lo, hi, length = l0, r0 + 1, 1
        while lo < hi:
            if lo & 1:
                self._setAll(lo, length, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._setAll(hi, length, v)
            lo >>= 1
            hi >>= 1
            length <<= 1
        self._recomputeToRoot(l0)
        self._recomputeToRoot(r0)

    # O(logN) -- (sm, pre, suf) of a[l..r], l <= r
    def _query(self, l, r):
        l += self.size
        r += self.size
        self._pushToRoot(l)
        self._pushToRoot(r)
        left = right = None
        r += 1
        while l < r:
            if l & 1:
                left = self._node(l) if left is None else self._merge(left, self._node(l))
                l += 1
            if r & 1:
                r -= 1
                right = self._node(r) if right is None else self._merge(self._node(r), right)
            l >>= 1
            r >>= 1
        if right is None:
            return left
        if left is None:
            return right
        return self._merge(left, right)

    # O(logN) -- max over l <= i <= r of a[l] + ... + a[i]
    def maxPrefixSum(self, l, r):
        return self._query(l, r)[1]

    # O(logN) -- max over l <= i <= r of a[i] + ... + a[r]
    def maxSuffixSum(self, l, r):
        return self._query(l, r)[2]

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._query(l, r)[0] if l <= r else 0

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.size
        self._pushToRoot(p)
        return self.sm[p]

    # O(N) -- the whole array: push every tag down one level at a time from the root, then read the leaves
    def getAll(self):
        H = self.H
        for s in range(H, 0, -1):
            for x in range(1 << (H - s), 1 << (H - s + 1)):
                self._push(x, 1 << (s - 1))
        return self.sm[self.size:self.size + self.n]

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAssign(i, i, val)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAssign(i, i, self.pointGet(i) + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.rangeAssign(i, i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.rangeAssign(i, i, val)
