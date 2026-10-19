# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeSum
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeAdd: log(U)
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: A[2*log(U)] B[2*log(U)]
#   tags: none
#   other: links[4*log(U)]
#   note: per update, the O(logU) entries above each changed position; a range add changes two points of A and B. Python: a Fenwick tree in a dict (no links); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases

# Range add + range sum: adding v on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[x] by
#   v * (x - l + 1) for x in [l, r], and the whole v * (r - l + 1) past r,
# so P(x) = A(x) + B(x) * x with A, B prefix sums of two arrays of point changes.
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a Fenwick tree in a
# dict keyed by offset x = i - lo, so only the O(logU) entries above changed positions exist.


class SparseRangeAddSumBIT:
    __slots__ = ("lo", "hi", "n", "d")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}

    # O(logU) -- (A, B)[x] += (v0, v1) at offset x
    def _add(self, x, v0, v1):
        d, n = self.d, self.n
        x += 1
        while x <= n:
            e = d.get(x)
            if e is None:
                d[x] = [v0, v1]
            else:
                e[0] += v0
                e[1] += v1
            x += x & -x

    # O(logU) -- prefix sums of (A, B) over offsets 0..x (zeros for x = -1)
    def _prefix(self, x):
        d = self.d
        s0 = s1 = 0
        x += 1
        while x > 0:
            e = d.get(x)
            if e is not None:
                s0 += e[0]
                s1 += e[1]
            x &= x - 1
        return s0, s1

    # O(logU) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        a = v * (1 - l)
        self._add(l, a, v)
        if r + 1 < self.n:
            self._add(r + 1, v * (r - l + 1) - a, -v)

    # O(logU) -- a[lo] + ... + a[lo + x] (0 for x = -1)
    def _sum(self, x):
        sa, sb = self._prefix(x)
        return sa + sb * x

    # O(logU) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        if l > r:
            return 0
        return self._sum(r - self.lo) - self._sum(l - 1 - self.lo)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self.rangeSum(i, i)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAdd(i, i, delta)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAdd(i, i, val - self.pointGet(i))

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.rangeAdd(i, i, val - cur)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.rangeAdd(i, i, val - cur)
