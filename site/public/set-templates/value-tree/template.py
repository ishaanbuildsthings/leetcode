# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/value-tree/template.py
# @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX
# @data-structure-type: value-tree
# @values: online-range
# @complexities:
#   add: log(U)
#   addCount: log(U)
#   count: log(U)
#   countDistinct: 1
#   countGtX: log(U)
#   countGteX: log(U)
#   countInValRange: log(U)
#   countLtX: log(U)
#   countLteX: log(U)
#   kthLargest: log(U)
#   kthSmallest: log(U)
#   largestLtX: log(U)
#   largestLteX: log(U)
#   max: 1
#   medianHigh: 1 amortized
#   medianLow: 1 amortized
#   min: 1
#   popMax: log(U)
#   popMin: log(U)
#   remove: log(U)
#   removeAll: log(U)
#   removeCount: log(U)
#   size: 1
#   smallestGtX: log(U)
#   smallestGteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: c[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per add of a new value, one node per level of its root path; U = hi - lo + 1. C++: one shared node pool (node 0 = empty), call resetPool() between test cases; Python: dicts keyed by heap index

# Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
# each node keeping how many copies are below it. Sparse: dicts keyed by heap
# index over a power-of-two cover of [lo, hi]; a missing key is an empty block. k-th / sums of the k smallest descend
# by counts.


class ValueTreeMultiset:
    __slots__ = ("lo", "hi", "cap", "c", "n", "mn", "mx", "med", "lowV", "lowB", "lowC", "highV", "highB", "highC", "d")

    # O(1) -- an empty multiset for values in [lo, hi] (any integers, negative is fine)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.cap = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of value v is cap + (v - lo)
        self.c = {}  # node -> copies below it
        self.med = False  # medians / mex are tracked from their first query on; min / max always (set by the first add)
        self.n = self.d = 0

    def _insert(self, x, c):
        cc = self.c
        i = self.cap + x - self.lo
        old = cc.get(i, 0)
        pres = (old + c > 0) - (old > 0)
        self.d += pres
        while i:
            cc[i] = cc.get(i, 0) + c
            i >>= 1

    def _prefix(self, f, x):  # f's total over the values < x
        if x <= self.lo:
            return 0
        if x > self.hi:
            return f.get(1, 0)
        i = self.cap + x - self.lo
        res = 0
        while i > 1:
            if i & 1:
                res += f.get(i - 1, 0)
            i >>= 1
        return res

    def _lt(self, x):
        return self._prefix(self.c, x)

    def _le(self, x):
        return self._prefix(self.c, x + 1)

    def _countOf(self, x):  # the leaf of x
        return self.c.get(self.cap + x - self.lo, 0) if self.lo <= x <= self.hi else 0

    def _kth(self, k):
        c, i, size = self.c, 1, self.cap
        while i < size:
            i <<= 1
            cl = c.get(i, 0)
            if k > cl:
                k -= cl
                i += 1
        return i - size + self.lo

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies)
        c, i, size, before = self.c, 1, self.cap, 0
        while i < size:
            i <<= 1
            cl = c.get(i, 0)
            if before + cl < k:
                before += cl
                i += 1
        return i - size + self.lo, before, c[i]


    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max (and medians / mex once asked for) current
        self.n += c
        self._insert(x, c)
        n = self.n
        if c > 0:
            if n == c:  # the set was empty
                self.mn = self.mx = x
                if self.med:
                    self.lowV = self.highV = x
                    self.lowB = self.highB = 0
                    self.lowC = self.highC = c
                return
            if x < self.mn:
                self.mn = x
            if x > self.mx:
                self.mx = x
        else:
            if not n:
                return
            if x == self.mn:
                self.mn = self._kth(1)
            if x == self.mx:
                self.mx = self._kth(n)
        if not self.med:
            return
        # each median is a tracked rank: shift its (value, copies before, copies), and search again only
        # when the rank leaves the tracked value
        if x < self.lowV:
            self.lowB += c
        elif x == self.lowV:
            self.lowC += c
        r = (n + 1) >> 1
        if not self.lowB < r <= self.lowB + self.lowC:
            self.lowV, self.lowB, self.lowC = self._kthInfo(r)
        if x < self.highV:
            self.highB += c
        elif x == self.highV:
            self.highC += c
        r = (n >> 1) + 1
        if not self.highB < r <= self.highB + self.highC:
            self.highV, self.highB, self.highC = self._kthInfo(r)

    def _startMedians(self):  # the first median query (n > 0): from now on _add keeps both medians current
        self.med = True
        n = self.n
        self.lowV, self.lowB, self.lowC = self._kthInfo((n + 1) >> 1)
        self.highV, self.highB, self.highC = self._kthInfo((n >> 1) + 1)

    # O(logU) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logU) -- add c copies of x (nothing if c <= 0)
    def addCount(self, x, c):
        if c > 0:
            self._add(x, c)

    # O(logU) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(logU) -- how many values > x
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(logU) -- how many values >= x
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(logU) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logU) -- how many values < x
    def countLtX(self, x):
        return self._lt(x)

    # O(logU) -- how many values <= x
    def countLteX(self, x):
        return self._le(x)

    # O(logU) -- k-th largest value (1-indexed); raises IndexError unless 1 <= k <= size
    def kthLargest(self, k):
        if not 1 <= k <= self.n:
            raise IndexError(f"kthLargest: needs 1 <= k <= size, got k = {k}, size = {self.n}")
        return self._kth(self.n - k + 1)

    # O(logU) -- k-th smallest value (1-indexed); raises IndexError unless 1 <= k <= size
    def kthSmallest(self, k):
        if not 1 <= k <= self.n:
            raise IndexError(f"kthSmallest: needs 1 <= k <= size, got k = {k}, size = {self.n}")
        return self._kth(k)

    # O(logU) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(logU) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        c = self._le(x)
        return self._kth(c) if c else None

    # O(1) -- largest value; None if empty
    def max(self):
        return self.mx if self.n else None

    # O(1 amortized) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        if not self.n:
            return None
        if not self.med:
            self._startMedians()
        return self.highV

    # O(1 amortized) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        if not self.n:
            return None
        if not self.med:
            self._startMedians()
        return self.lowV

    # O(1) -- smallest value; None if empty
    def min(self):
        return self.mn if self.n else None

    # O(logU) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self.mx
        self._add(v, -1)
        return v

    # O(logU) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self.mn
        self._add(v, -1)
        return v

    # O(logU) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self.count(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logU) -- remove every copy of x; returns how many were removed
    def removeAll(self, x):
        k = self.count(x)
        if k:
            self._add(x, -k)
        return k

    # O(logU) -- remove min(c, count(x)) copies of x; returns how many were removed
    def removeCount(self, x, c):
        k = min(c, self.count(x))
        if k <= 0:
            return 0
        self._add(x, -k)
        return k

    # O(1) -- how many values (copies count)
    def size(self):
        return self.n

    # O(logU) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logU) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None
