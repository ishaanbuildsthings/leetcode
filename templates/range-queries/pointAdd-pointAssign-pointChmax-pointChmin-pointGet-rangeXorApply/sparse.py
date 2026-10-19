# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeXorApply
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeXorApply: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: d[2*log(U)]
#   tags: none
#   other: links[4*log(U)]
#   note: per update, the O(logU) entries above each changed position; a range xor changes two xor-differences. Python: a Fenwick tree in a dict (no links); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases

# Range xor, point get: prefix xors of the xor-difference array d[i] = a[i] ^ a[i - 1].
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a Fenwick tree in a
# dict keyed by offset x = i - lo, so only the O(logU) entries above changed positions exist.


class SparseRangeXorBIT:
    __slots__ = ("lo", "hi", "n", "d")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}

    # O(logU) -- d[x] += v at offset x
    def _add(self, x, v):
        d, n = self.d, self.n
        x += 1
        while x <= n:
            d[x] = d.get(x, 0) ^ v
            x += x & -x

    # O(logU) -- d[0] + ... + d[x] (0 for x = -1)
    def _prefix(self, x):
        d = self.d
        s = 0
        x += 1
        while x > 0:
            s ^= d.get(x, 0)
            x &= x - 1
        return s

    # O(logU) -- a[i] ^= x for i in [l, r]
    def rangeXorApply(self, l, r, x):
        if l > r:
            return
        self._add(l - self.lo, x)
        if r < self.hi:
            self._add(r + 1 - self.lo, x)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._prefix(i - self.lo)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        d = self.pointGet(i) ^ val
        if d:
            self.rangeXorApply(i, i, d)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.rangeXorApply(i, i, cur ^ val)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.rangeXorApply(i, i, cur ^ val)
