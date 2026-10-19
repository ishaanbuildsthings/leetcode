# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeSum
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeSum: log(N)
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

    # O(logN) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        if l > r:
            return
        self._addDiff(l, v)
        if r + 1 < self.n:
            self._addDiff(r + 1, -v)

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._prefix(r) - self._prefix(l - 1) if l <= r else 0

    # O(logN) -- a[i]
    def pointGet(self, i):
        return self.rangeSum(i, i)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAdd(i, i, delta)

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAdd(i, i, val - self.pointGet(i))

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.rangeAdd(i, i, val - cur)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.rangeAdd(i, i, val - cur)
