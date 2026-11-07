# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxPrefixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/template.py
# @operations: getAll maxPrefixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum sumAll
# @data-structure-type: seg-tree
# @letters: same
# @complexities:
#   getAll: N
#   maxPrefixSum: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   rangeSum: log(N)
#   sumAll: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] pre[2*N]
#   tags: none
#   other: none
#   note: each node is (sum, best prefix); the merge is not commutative, so a query folds a left and a right accumulator

# Max prefix sum of a range, plus range sum, with point updates. All indices 0-based, ranges
# inclusive [l, r]. Maxima are over NON-EMPTY pieces; when the empty piece is allowed (answer >= 0), take max(0, ...).
# Iterative 2N tree. The merge is not commutative, so a query folds nodes into a left accumulator (left to right)
# and a right accumulator (right to left), then joins the two. Leaner than the max subarray tree: only
# (sm, pre) per node.


class MaxPrefixSumTree:
    __slots__ = ("n", "sm", "pre")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.sm = [0] * n + list(arr)
        self.pre = [0] * n + list(arr)
        for x in range(n - 1, 0, -1):
            self._pull(x)

    @staticmethod
    def _merge(a, b):
        sm = a[0] + b[0]
        pre = a[1] if a[1] > a[0] + b[1] else a[0] + b[1]
        return sm, pre

    def _node(self, x):
        return self.sm[x], self.pre[x]

    def _pull(self, x):
        self.sm[x], self.pre[x] = self._merge(self._node(2 * x), self._node(2 * x + 1))

    # O(logN) -- (sm, pre) of a[l..r], l <= r
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

    # O(logN) -- max over l <= i <= r of a[l] + ... + a[i]; needs 0 <= l <= r < n, else IndexError
    def maxPrefixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxPrefixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._query(l, r)[1]

    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._query(l, r)[0] if l <= r else 0

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self.sm[p] = self.pre[p] = val
        p >>= 1
        while p:
            self._pull(p)
            p >>= 1

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.sm[i + self.n]

    # O(N) -- the whole array (a copy of the leaves)
    def getAll(self):
        return self.sm[self.n:]

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.sm[i + self.n] + delta)

    # O(logN) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.sm[i + self.n]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val); needs needs 0 <= i < n, else IndexError, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.sm[i + self.n]:
            self.pointAssign(i, val)
