# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countValue-kthOccurrence-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/sparse.py
# @operations: countValue kthOccurrence pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: BIT
# @complexities:
#   countValue: log(U)
#   kthOccurrence: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: cnt[1*log(U)]
#   tags: none
#   other: children[2*log(U)] vals[1]
#   note: per point write, the O(logU) entries above it; position i stores [a[i] == number] - [0 == number], so the untouched store nothing; kthOccurrence descends / binary-lifts. A Fenwick tree in a dict

# Count / find the k-th occurrence of one value (fixed at build time) in a range, with point updates, over any index
# range [lo, hi] (huge or negative is fine); every position starts at 0. An index counts if a[i] == number; untouched
# positions count iff number == 0 (z below), so position i stores [a[i] == number] - z in a dict Fenwick tree and a
# count over k positions is z * k plus the stored sum. kthOccurrence binary-lifts over the tree.


class SparseCountValueBIT:
    __slots__ = ("lo", "hi", "n", "d", "vals", "number", "z")

    # O(1)
    def __init__(self, lo, hi, number):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}
        self.vals = {}  # i -> a[i], nonzero values only
        self.number = number
        self.z = int(number == 0)

    # O(logU) -- the change v at position i, into the Fenwick tree over offsets
    def _add(self, i, v):
        d, n = self.d, self.n
        x = i - self.lo + 1
        while x <= n:
            d[x] = d.get(x, 0) + v
            x += x & -x

    # O(logU) -- total of the changes at positions lo..i (0 for i < lo)
    def _prefix(self, i):
        d = self.d
        s = 0
        x = i - self.lo + 1
        while x > 0:
            s += d.get(x, 0)
            x &= x - 1
        return s

    # O(logU) -- how many i in [lo, i] have a[i] == number
    def _count(self, i):
        return self.z * (i - self.lo + 1) + self._prefix(i)

    # O(logU) -- how many i in [l, r] have a[i] == number
    def countValue(self, l, r):
        return self._count(r) - self._count(l - 1) if l <= r else 0

    # O(logU) -- index of the k-th (1-indexed) i in [l, r] with a[i] == number, or lo - 1
    def kthOccurrence(self, l, r, k):
        if k <= 0 or k > self.countValue(l, r):
            return self.lo - 1
        target = self._count(l - 1) + k
        d, n, z = self.d, self.n, self.z
        pos = acc = 0
        step = 1 << (n.bit_length() - 1)
        while step:
            nxt = pos + step
            if nxt <= n:  # Fenwick node nxt covers the step offsets after pos
                v = acc + d.get(nxt, 0) + z * step
                if v < target:
                    pos, acc = nxt, v
            step >>= 1
        return self.lo + pos

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        old = self.vals.get(i, 0)
        diff = (val == self.number) - (old == self.number)
        if val:
            self.vals[i] = val
        else:
            self.vals.pop(i, None)
        if diff:
            self._add(i, diff)

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
