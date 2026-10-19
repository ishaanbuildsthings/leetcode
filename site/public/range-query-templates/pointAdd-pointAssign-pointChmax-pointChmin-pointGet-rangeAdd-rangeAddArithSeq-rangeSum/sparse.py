# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAddArithSeq rangeSum
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeAdd: log(U)
#   rangeAddArithSeq: log(U)
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: A[2*log(U)] B[2*log(U)] C[2*log(U)]
#   tags: none
#   other: links[4*log(U)]
#   note: per update, the O(logU) entries above each changed position; an arithmetic-sequence add changes two points of A, B and C. Python: a Fenwick tree in a dict (no links); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases


def _tri(k):
    return k * (k + 1) // 2

# Range add of an arithmetic sequence (and plain range add) + range sum. Adding c0 + c1 * x (x = i - lo)
# on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[lo + x] by c0 * (x - l + 1) + c1 * (tri(x) - tri(l - 1))
# for x in [l, r] (tri(k) = k(k+1)/2), and by the whole added total past r. So P(x) = A(x) + B(x) * x +
# C(x) * tri(x) with A, B, C prefix sums of point changes; tri keeps every coefficient an integer.
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a Fenwick tree in a
# dict keyed by offset x = i - lo, so only the O(logU) entries above changed positions exist.


class SparseArithSeqSumBIT:
    __slots__ = ("lo", "hi", "n", "d")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}

    # O(logU) -- (A, B, C)[x] += (v0, v1, v2) at offset x
    def _add(self, x, v0, v1, v2):
        d, n = self.d, self.n
        x += 1
        while x <= n:
            e = d.get(x)
            if e is None:
                d[x] = [v0, v1, v2]
            else:
                e[0] += v0
                e[1] += v1
                e[2] += v2
            x += x & -x

    # O(logU) -- prefix sums of (A, B, C) over offsets 0..x (zeros for x = -1)
    def _prefix(self, x):
        d = self.d
        s0 = s1 = s2 = 0
        x += 1
        while x > 0:
            e = d.get(x)
            if e is not None:
                s0 += e[0]
                s1 += e[1]
                s2 += e[2]
            x &= x - 1
        return s0, s1, s2

    # O(logU) -- a[l + j] += start + j * step for j in [0, r - l]
    def rangeAddArithSeq(self, l, r, start, step):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        c0, c1 = start - step * l, step  # adding c0 + c1 * x at offset x
        a = c0 * (1 - l) - c1 * _tri(l - 1)
        self._add(l, a, c0, c1)
        if r + 1 < self.n:
            total = c0 * (r - l + 1) + c1 * (_tri(r) - _tri(l - 1))
            self._add(r + 1, total - a, -c0, -c1)

    # O(logU) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        self.rangeAddArithSeq(l, r, v, 0)

    # O(logU) -- a[lo] + ... + a[lo + x] (0 for x = -1)
    def _sum(self, x):
        sa, sb, sc = self._prefix(x)
        return sa + sb * x + sc * _tri(x)

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
