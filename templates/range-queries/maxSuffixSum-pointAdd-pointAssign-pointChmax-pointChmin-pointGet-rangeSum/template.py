# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/template.py
# @operations: maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
# @data-structure-type: seg-tree
# @complexities:
#   maxSuffixSum: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] suf[2*N]
#   tags: none
#   other: none
#   note: each node is (sum, best suffix); the merge is not commutative, so a query folds a left and a right accumulator

# Max suffix sum of a range, plus range sum, with point updates. All indices 0-based, ranges
# inclusive [l, r]. Maxima are over NON-EMPTY pieces; when the empty piece is allowed (answer >= 0), take max(0, ...).
# Iterative 2N tree. The merge is not commutative, so a query folds nodes into a left accumulator (left to right)
# and a right accumulator (right to left), then joins the two. Leaner than the max subarray tree: only
# (sm, suf) per node.


class MaxSuffixSumTree:
    __slots__ = ("n", "sm", "suf")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.sm = [0] * n + list(arr)
        self.suf = [0] * n + list(arr)
        for x in range(n - 1, 0, -1):
            self._pull(x)

    @staticmethod
    def _merge(a, b):
        sm = a[0] + b[0]
        suf = b[1] if b[1] > b[0] + a[1] else b[0] + a[1]
        return sm, suf

    def _node(self, x):
        return self.sm[x], self.suf[x]

    def _pull(self, x):
        self.sm[x], self.suf[x] = self._merge(self._node(2 * x), self._node(2 * x + 1))

    # O(logN) -- (sm, suf) of a[l..r], l <= r
    def _query(self, l, r):
        left = right = None
        l += self.n
        r += self.n + 1
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

    # O(logN) -- max over l <= i <= r of a[i] + ... + a[r]
    def maxSuffixSum(self, l, r):
        return self._query(l, r)[1]

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._query(l, r)[0] if l <= r else 0

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        p = i + self.n
        self.sm[p] = self.suf[p] = val
        p >>= 1
        while p:
            self._pull(p)
            p >>= 1

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.sm[i + self.n]

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.sm[i + self.n] + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.sm[i + self.n]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.sm[i + self.n]:
            self.pointAssign(i, val)
