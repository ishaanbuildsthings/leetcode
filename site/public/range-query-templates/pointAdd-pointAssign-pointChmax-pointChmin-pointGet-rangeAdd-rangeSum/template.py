# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeSum/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeSum sumAll
# @data-structure-type: BIT
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeSum: log(N)
#   sumAll: log(N)
#   build: N
# @memory:
#   layout: none
#   node: b1[1*N] b2[1*N]
#   tags: none
#   other: none
#   note: two Fenwick trees over the difference array d (d[i] = a[i] - a[i-1]): b1 over d[i], b2 over d[i] * i

# Range add + range sum with two Fenwick trees, no lazy tags. All indices 0-based, ranges inclusive [l, r].
# With d the difference array, a[0] + ... + a[x] = (x + 1) * sum(d[0..x]) - sum(d[i] * i for i in 0..x),
# so one BIT over d[i] and one over d[i] * i answer any prefix sum, and a range add touches two entries of d.


class RangeAddSumBIT:
    __slots__ = ("n", "b1", "b2")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        b1 = self.b1 = [0] * (n + 1)
        b2 = self.b2 = [0] * (n + 1)
        prev = 0
        for i, v in enumerate(arr):
            d = v - prev
            prev = v
            b1[i + 1] = d
            b2[i + 1] = d * i
        for i in range(1, n + 1):
            j = i + (i & -i)
            if j <= n:
                b1[j] += b1[i]
                b2[j] += b2[i]

    def _addDiff(self, i, d):
        b1, b2, n = self.b1, self.b2, self.n
        di = d * i
        i += 1
        while i <= n:
            b1[i] += d
            b2[i] += di
            i += i & -i

    # O(logN) -- a[0] + ... + a[x] (0 for x = -1)
    def _prefix(self, x):
        b1, b2 = self.b1, self.b2
        s1 = s2 = 0
        i = x + 1
        while i > 0:
            s1 += b1[i]
            s2 += b2[i]
            i &= i - 1
        return s1 * (x + 1) - s2

    # O(logN) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return
        self._addDiff(l, v)
        if r + 1 < self.n:
            self._addDiff(r + 1, -v)

    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._prefix(r) - self._prefix(l - 1) if l <= r else 0

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.rangeSum(i, i)

    # O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    # i + lowbit(i) once complete), then one pass of running prefix sums
    def getAll(self):
        n = self.n
        b1, b2 = self.b1[:], self.b2[:]
        for i in range(n, 0, -1):
            j = i + (i & -i)
            if j <= n:
                b1[j] -= b1[i]
                b2[j] -= b2[i]
        out = []
        s1 = s2 = prev = 0
        for x in range(n):
            s1 += b1[x + 1]
            s2 += b2[x + 1]
            p = s1 * (x + 1) - s2
            out.append(p - prev)
            prev = p
        return out

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAdd(i, i, delta)

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAdd(i, i, val - self.pointGet(i))

    # O(logN) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        cur = self.pointGet(i)
        if val > cur:
            self.rangeAdd(i, i, val - cur)

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
        cur = self.pointGet(i)
        if val < cur:
            self.rangeAdd(i, i, val - cur)
