# @operations: doAllElementsAppearEvenFrequency pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: BIT
# @complexities:
#   doAllElementsAppearEvenFrequency: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: 1
#   build: 1
# @memory:
#   layout: sparse
#   node: h[1*log(U)]
#   tags: none
#   other: links[2*log(U)] vals[1] tag[1]
#   note: per point write, the O(logU) entries above it; every value has a random 64-bit tag and position i stores tag(a[i]) ^ tag(0), so untouched positions store nothing and a range adds tag(0) once per odd length. Python: a Fenwick tree in a dict; C++: a dynamic prefix-xor tree in one shared node pool, call resetPool() between test cases

import random

# Range "does every value appear an even number of times?" via xor hashing, with point updates, over any index
# range [lo, hi] (huge or negative is fine); every position starts at 0. Each distinct value gets a random 64-bit
# tag; xor over a range cancels tags in pairs, so an all-even range hashes to 0 (false positives ~q / 2^64).
# Sparse: position i stores tag(a[i]) ^ tag(0) in a dict Fenwick tree (0 for the untouched), so the xor of the
# real tags over [l, r] is the stored xor, plus tag(0) when the length is odd.


class SparseXorEven:
    __slots__ = ("lo", "hi", "n", "d", "vals", "tag", "zero")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}
        self.vals = {}  # i -> a[i], nonzero values only
        self.tag = {}
        self.zero = self._tagOf(0)

    # O(1) -- random tag for a value, minted on first sight
    def _tagOf(self, v):
        t = self.tag.get(v)
        if t is None:
            t = self.tag[v] = random.getrandbits(64)
        return t

    # O(logU) -- the change v at position i, into the Fenwick tree over offsets
    def _add(self, i, v):
        d, n = self.d, self.n
        x = i - self.lo + 1
        while x <= n:
            d[x] = d.get(x, 0) ^ v
            x += x & -x

    # O(logU) -- total of the changes at positions lo..i (0 for i < lo)
    def _prefix(self, i):
        d = self.d
        s = 0
        x = i - self.lo + 1
        while x > 0:
            s ^= d.get(x, 0)
            x &= x - 1
        return s

    # O(logU) -- True iff every value in a[l..r] appears an even number of times
    def doAllElementsAppearEvenFrequency(self, l, r):
        h = self._prefix(r) ^ self._prefix(l - 1)
        if (r - l + 1) & 1:
            h ^= self.zero
        return h == 0

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        d = self._tagOf(self.vals.get(i, 0)) ^ self._tagOf(val)
        if val:
            self.vals[i] = val
        else:
            self.vals.pop(i, None)
        if d:
            self._add(i, d)

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.vals.get(i, 0)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
