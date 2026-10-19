# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAddArithSeq
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeAdd: log(U)
#   rangeAddArithSeq: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: c[2*log(U)] s[2*log(U)]
#   tags: none
#   other: links[4*log(U)]
#   note: per update, the O(logU) entries above each changed position; an arithmetic-sequence add changes two points of c and s. Python: a Fenwick tree in a dict (no links); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases

# Range add of an arithmetic sequence (and plain range add), point get. Adding start + (i - l) * step on
# [l, r] is adding the line c0 + c1 * x (x = i - lo), so a[x] = C(x) + x * S(x) with C, S prefix sums of
# two difference arrays.
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a Fenwick tree in a
# dict keyed by offset x = i - lo, so only the O(logU) entries above changed positions exist.


class SparseArithSeqBIT:
    __slots__ = ("lo", "hi", "n", "d")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}

    # O(logU) -- (c, s)[x] += (v0, v1) at offset x
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

    # O(logU) -- prefix sums of (c, s) over offsets 0..x (zeros for x = -1)
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

    # O(logU) -- a[l + j] += start + j * step for j in [0, r - l]
    def rangeAddArithSeq(self, l, r, start, step):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        c0 = start - step * l
        self._add(l, c0, step)
        if r + 1 < self.n:
            self._add(r + 1, -c0, -step)

    # O(logU) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        self.rangeAddArithSeq(l, r, v, 0)

    # O(logU) -- a[i]
    def pointGet(self, i):
        x = i - self.lo
        c, s = self._prefix(x)
        return c + s * x

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
