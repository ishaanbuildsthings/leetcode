# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/value-tree-with-sums-or-mex-mode/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min mode orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: value-tree
# @values: online-range
# @keys: numbers
# @tracks: mode
# @complexities:
#   add: log(U)
#   addCount: log(U)
#   clear: N*log(U)
#   count: log(U)
#   countDistinct: 1
#   countDistinctInValRange: log(U)
#   countGtX: log(U)
#   countGteX: log(U)
#   countInValRange: log(U)
#   countLtX: log(U)
#   countLteX: log(U)
#   firstIndex: log(U)
#   kth: log(U)
#   largestLtX: log(U)
#   largestLteX: log(U)
#   lastIndex: log(U)
#   max: log(U)
#   medianHigh: log(U)
#   medianLow: log(U)
#   mex: log(U)
#   min: log(U)
#   mode: 1
#   orOfAll: 1
#   orOfGtX: log(U)
#   orOfGteX: log(U)
#   orOfInValRange: log(U)
#   orOfKthLargestRange: log(U)
#   orOfKthSmallestRange: log(U)
#   orOfLargestK: log(U)
#   orOfLtX: log(U)
#   orOfLteX: log(U)
#   orOfSmallestK: log(U)
#   pop: log(U)
#   popMax: log(U)
#   popMin: log(U)
#   remove: log(U)
#   removeAll: log(U)
#   removeCount: log(U)
#   removeInValRange: log(U) amortized
#   size: 1
#   smallestGtX: log(U)
#   smallestGteX: log(U)
#   sumAbsDiffToMedian: log(U)
#   sumAbsDiffToX: log(U)
#   sumAll: 1
#   sumGtX: log(U)
#   sumGteX: log(U)
#   sumInValRange: log(U)
#   sumKthLargestRange: log(U)
#   sumKthSmallestRange: log(U)
#   sumLargestK: log(U)
#   sumLtX: log(U)
#   sumLteX: log(U)
#   sumSmallestK: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: c[1*log(U)] p[1*log(U)] s[1*log(U)] o[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per add of a new value, one node per level of its root path; U = hi - lo + 1. C++: each multiset owns its node pool (node 0 = empty); Python: dicts keyed by heap index

# Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
# each node keeping how many copies, their sum,, their OR and how many distinct values (for mex) are below it. Sparse: dicts keyed by heap
# index over a power-of-two cover of [lo, hi]; a missing key is an empty block. k-th / sums of the k smallest descend
# by counts; mex descends to the first value >= 0 whose block isn't full.


class ValueTreeMultiset:
    __slots__ = ("lo", "hi", "cap", "c", "s", "o", "p", "n", "bk", "maxF", "total", "d")

    # O(1) -- an empty multiset for values in [lo, hi] (any integers, negative is fine)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.cap = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of value v is cap + (v - lo)
        self.c = {}  # node -> copies below it
        self.s = {}  # node -> sum of the copies below it
        self.p = {}  # node -> distinct values below it
        self.o = {}  # node -> OR of the values below it
        self.bk, self.maxF = {}, 0  # mode: count -> the values with that many copies; the highest count
        self.n = self.total = self.d = 0

    def _insert(self, x, c):
        cc, ss = self.c, self.s
        pp = self.p
        oo = self.o
        i = self.cap + x - self.lo
        old = cc.get(i, 0)
        pres = (old + c > 0) - (old > 0)
        self.d += pres
        ov = x if old + c > 0 else 0  # the OR below the current node
        while i:
            cc[i] = cc.get(i, 0) + c
            ss[i] = ss.get(i, 0) + c * x
            if pres:
                pp[i] = pp.get(i, 0) + pres
            if pres:  # x appeared or disappeared: the OR / AND up its path, each node with its sibling's
                oo[i] = ov
                ov |= oo.get(i ^ 1, 0)
            i >>= 1
        return old + c  # (x's new count)

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

    def _slt(self, x):
        return self._prefix(self.s, x)

    def _sle(self, x):
        return self._prefix(self.s, x + 1)

    def _kth(self, k):
        c, i, size = self.c, 1, self.cap
        while i < size:
            i <<= 1
            cl = c.get(i, 0)
            if k > cl:
                k -= cl
                i += 1
        return i - size + self.lo

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies, sum before it)
        c, s, i, size, before, acc = self.c, self.s, 1, self.cap, 0, 0
        while i < size:
            i <<= 1
            cl = c.get(i, 0)
            if before + cl < k:
                before += cl
                acc += s.get(i, 0)
                i += 1
        return i - size + self.lo, before, c[i], acc

    # smallest non-negative integer not in the set (hi + 1 if all of [0, hi] are present)
    def _findMex(self):
        if self.lo > 0:
            return 0
        p, size = self.p, self.cap

        def full(i):  # every value below node i is present
            return p.get(i, 0) == size >> (i.bit_length() - 1)

        i = size - self.lo  # the leaf of value 0
        while True:
            while i > 1 and not i & 1:  # climb while i is a left child: its parent starts at the same value
                i >>= 1
            if not full(i):  # the first missing value is inside i: descend, preferring the left child
                while i < size:
                    i <<= 1
                    if full(i):
                        i += 1
                return min(i - size + self.lo, self.hi + 1)
            i += 1
            if not i & (i - 1):  # walked off the right edge
                return self.hi + 1

    def _add(self, x, c):  # c copies of x (c < 0 removes)
        self.n += c
        self.total += c * x
        f = self._insert(x, c)  # x's new count
        g = f - c  # x's old count
        # mode: x moves from the bucket of its old count to its new one
        bk = self.bk
        if g:
            vs = bk[g]
            vs.discard(x)
            if not vs:
                del bk[g]
        if f:
            if f in bk:
                bk[f].add(x)
            else:
                bk[f] = {x}
            if f > self.maxF:
                self.maxF = f
        while self.maxF and self.maxF not in bk:  # (it only drops as far as copies were removed: amortized O(1))
            self.maxF -= 1

    def _sumFirst(self, k):  # sum of the k smallest values
        if k <= 0:
            return 0
        v, b, _, s = self._kthInfo(k)
        return s + (k - b) * v

    def _resetCached(self):  # nothing counted: as newly built
        self.bk, self.maxF = {}, 0
        self.n = self.d = 0
        self.total = 0

    def _clearData(self):
        self.c = {}
        self.s = {}
        self.p = {}
        self.o = {}

    def _distinctLt(self, x):  # distinct values < x
        return self._prefix(self.p, x)

    def _orIn(self, lo, hi):  # OR of the values in [lo, hi]: bottom-up over the heap-indexed blocks
        lo, hi = max(lo, self.lo), min(hi, self.hi)
        if lo > hi:
            return 0
        f, res = self.o, 0
        l, r = self.cap + lo - self.lo, self.cap + hi - self.lo + 1
        while l < r:
            if l & 1:
                res |= f.get(l, 0)
                l += 1
            if r & 1:
                r -= 1
                res |= f.get(r, 0)
            l >>= 1
            r >>= 1
        return res

    def _orLe(self, x):  # OR of the values <= x
        return self._orIn(self.lo, x)

    def _orGe(self, x):  # OR of the values >= x
        return self._orIn(x, self.hi)

    # O(logU) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logU) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(N logU) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logU) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(logU) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    def countDistinctInValRange(self, lo, hi):
        if lo > hi:
            return 0
        return self._distinctLt(hi) - self._distinctLt(lo) + (1 if self._countOf(hi) else 0)

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

    # O(logU) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(logU) -- the value at sorted position i (0-indexed: kth(0) is the min); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1)

    # O(logU) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(logU) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        c = self._le(x)
        return self._kth(c) if c else None

    # O(logU) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(logU) -- largest value; None if empty
    def max(self):
        return self._kth(self.n) if self.n else None

    # O(logU) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        return self._kth((self.n >> 1) + 1) if self.n else None

    # O(logU) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        return self._kth((self.n + 1) >> 1) if self.n else None

    # O(logU) -- smallest non-negative integer not in the set
    def mex(self):
        return self._findMex()

    # O(logU) -- smallest value; None if empty
    def min(self):
        return self._kth(1) if self.n else None

    # O(1) -- (a most frequent value, its count); None if empty. C++ returns the smallest of the most frequent values
    def mode(self):
        if not self.n:
            return None
        f = self.maxF
        return next(iter(self.bk[f])), f

    # O(1) -- bitwise OR of all values; 0 if empty
    def orOfAll(self):
        return self.o.get(1, 0)

    # O(logU) -- bitwise OR of the values > x; 0 if there are none
    def orOfGtX(self, x):
        return self._orGe(x + 1)

    # O(logU) -- bitwise OR of the values >= x; 0 if there are none
    def orOfGteX(self, x):
        return self._orGe(x)

    # O(logU) -- bitwise OR of the values v with lo <= v <= hi; 0 if there are none
    def orOfInValRange(self, lo, hi):
        return self._orIn(lo, hi) if lo <= hi else 0

    # O(logU) -- bitwise OR of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._orIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logU) -- bitwise OR of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._orIn(self._kth(kFrom), self._kth(kTo))

    # O(logU) -- bitwise OR of the k largest values (0 for k = 0); raises IndexError unless 0 <= k <= size
    def orOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orGe(self._kth(self.n - k + 1)) if k else 0

    # O(logU) -- bitwise OR of the values < x; 0 if there are none
    def orOfLtX(self, x):
        return self._orLe(x - 1)

    # O(logU) -- bitwise OR of the values <= x; 0 if there are none
    def orOfLteX(self, x):
        return self._orLe(x)

    # O(logU) -- bitwise OR of the k smallest values (0 for k = 0); raises IndexError unless 0 <= k <= size
    def orOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orLe(self._kth(k)) if k else 0

    # O(logU) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logU) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(logU) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self._kth(1)
        self._add(v, -1)
        return v

    # O(logU) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self.count(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logU) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logU) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(logU amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    def removeInValRange(self, lo, hi):
        if lo > hi:
            return 0
        removed = 0
        while self.n:  # the smallest value >= lo, while it is <= hi: drop all its copies
            c = self._lt(lo)
            if c == self.n:
                break
            v = self._kth(c + 1)
            if v > hi:
                break
            k = self._countOf(v)
            self._add(v, -k)
            removed += k
        return removed

    # O(1) -- how many values (copies count)
    def size(self):
        return self.n

    # O(1) -- same as size()
    def __len__(self):
        return self.n

    # O(logU) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logU) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logU) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    def sumAbsDiffToMedian(self):
        if not self.n:
            return 0
        v, b, c, s = self._kthInfo((self.n + 1) >> 1)
        return v * b - s + (self.total - s - c * v) - v * (self.n - b - c)

    # O(logU) -- sum of |v - x| over all values
    def sumAbsDiffToX(self, x):
        c, s = self._lt(x), self._slt(x)
        return x * c - s + (self.total - s) - x * (self.n - c)

    # O(1) -- sum of all values
    def sumAll(self):
        return self.total

    # O(logU) -- sum of the values > x
    def sumGtX(self, x):
        return self.total - self._sle(x)

    # O(logU) -- sum of the values >= x
    def sumGteX(self, x):
        return self.total - self._slt(x)

    # O(logU) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    def sumInValRange(self, lo, hi):
        return self._sle(hi) - self._slt(lo) if lo <= hi else 0

    # O(logU) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); raises IndexError unless 1 <= kFrom <= kTo <= size
    def sumKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._sumFirst(self.n - kFrom + 1) - self._sumFirst(self.n - kTo)

    # O(logU) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def sumKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._sumFirst(kTo) - self._sumFirst(kFrom - 1)

    # O(logU) -- sum of the k largest values; raises IndexError unless 0 <= k <= size
    def sumLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.total - self._sumFirst(self.n - k)

    # O(logU) -- sum of the values < x
    def sumLtX(self, x):
        return self._slt(x)

    # O(logU) -- sum of the values <= x
    def sumLteX(self, x):
        return self._sle(x)

    # O(logU) -- sum of the k smallest values; raises IndexError unless 0 <= k <= size
    def sumSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._sumFirst(k)
