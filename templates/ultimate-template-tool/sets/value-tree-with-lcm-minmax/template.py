# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/value-tree-with-lcm-minmax/template.py
# @operations: add addCount clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex lcmOfAll lcmOfGtX lcmOfGteX lcmOfInValRange lcmOfKthLargestRange lcmOfKthSmallestRange lcmOfLargestK lcmOfLtX lcmOfLteX lcmOfSmallestK max medianHigh medianLow min pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
# @data-structure-type: value-tree
# @values: online-range
# @keys: numbers
# @tracks: minmax
# @complexities:
#   add: log(U)*log(U)
#   addCount: log(U)*log(U)
#   lcmOfAll: 1
#   lcmOfGtX: log(U)*log(U)
#   lcmOfGteX: log(U)*log(U)
#   lcmOfInValRange: log(U)*log(U)
#   lcmOfKthLargestRange: log(U)*log(U)
#   lcmOfKthSmallestRange: log(U)*log(U)
#   lcmOfLargestK: log(U)*log(U)
#   lcmOfLtX: log(U)*log(U)
#   lcmOfLteX: log(U)*log(U)
#   lcmOfSmallestK: log(U)*log(U)
#   clear: 1 amortized
#   count: log(U)
#   countDistinct: 1
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
#   max: 1
#   medianHigh: log(U)
#   medianLow: log(U)
#   min: 1
#   pop: log(U)*log(U)
#   popMax: log(U)*log(U)
#   popMin: log(U)*log(U)
#   remove: log(U)*log(U)
#   removeAll: log(U)*log(U)
#   removeCount: log(U)*log(U)
#   removeInValRange: log(U)*log(U) amortized
#   size: 1
#   smallestGtX: log(U)
#   smallestGteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: c[1*log(U)] m[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per add of a new value, one node per level of its root path; U = hi - lo + 1. C++: each multiset owns its node pool (node 0 = empty); Python: dicts keyed by heap index
# lcmOf... answers -1 once the LCM passes cap, so it never overflows: cap is a constructor argument, the largest
# value (2**63 - 1) by default; pass your own, e.g. ValueTreeMultiset(lo, hi, cap=10**9). Removing values is safe:
# every node keeps the capped LCM of just its own values, so once the values that pushed it past cap are gone,
# lcmOf... is exact again. Values must be >= 0. An empty selection gives the identity: gcd 0, LCM 1.

# Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
# each node keeping how many copies, their LCM are below it. Sparse: dicts keyed by heap
# index over a power-of-two cover of [lo, hi]; a missing key is an empty block. k-th / sums of the k smallest descend
# by counts.


from math import gcd
class ValueTreeMultiset:
    __slots__ = ("lo", "hi", "B", "L", "R", "c", "m", "n", "mn", "mx", "d", "cap")

    # O(1) -- an empty multiset for values in [lo, hi] (any integers, negative is fine)
    def __init__(self, lo, hi, cap=2**63 - 1):
        self.cap = cap
        self.lo, self.hi = lo, hi
        self.B = (hi - lo).bit_length()  # levels below the root: a value's path is the bits of v - lo, highest first
        self._clearData()
        self.n = self.d = 0

    def _newNode(self):
        self.L.append(0)
        self.R.append(0)
        self.c.append(0)
        self.m.append(1)
        return len(self.L) - 1

    def _insert(self, x, c):
        L, R, cc = self.L, self.R, self.c
        off, t, path = x - self.lo, 1, [1]
        for h in range(self.B - 1, -1, -1):
            kids = R if off >> h & 1 else L
            nxt = kids[t]
            if not nxt:
                nxt = kids[t] = self._newNode()
            t = nxt
            path.append(t)
        old = cc[t]
        pres = (old + c > 0) - (old > 0)
        self.d += pres
        for i in path:
            cc[i] += c
        if pres:  # x appeared or disappeared: the gcd / LCM up its path, each node from its two children
            mm = self.m
            mm[t] = self._lc(1, x) if old + c > 0 else 1
            for i in reversed(path[:-1]):
                mm[i] = self._lc(mm[L[i]], mm[R[i]])
        return old + c  # (x's new count)

    def _prefix(self, f, x):  # f's total over the values < x
        if x <= self.lo:
            return 0
        if x > self.hi:
            return f[1]
        L, R, off, t, res = self.L, self.R, x - self.lo, 1, 0
        for h in range(self.B - 1, -1, -1):
            if off >> h & 1:
                res += f[L[t]]
                t = R[t]
            else:
                t = L[t]
            if not t:
                break
        return res

    def _lt(self, x):
        return self._prefix(self.c, x)

    def _le(self, x):
        return self._prefix(self.c, x + 1)

    def _countOf(self, x):  # the leaf of x
        if not self.lo <= x <= self.hi:
            return 0
        L, R, off, t = self.L, self.R, x - self.lo, 1
        for h in range(self.B - 1, -1, -1):
            t = R[t] if off >> h & 1 else L[t]
            if not t:
                return 0
        return self.c[t]

    def _kth(self, k):
        L, R, c, t, v = self.L, self.R, self.c, 1, 0
        for h in range(self.B - 1, -1, -1):
            l = L[t]
            cl = c[l]
            if k > cl:
                k -= cl
                t = R[t]
                v |= 1 << h
            else:
                t = l
        return v + self.lo

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies)
        L, R, c, t, v, before = self.L, self.R, self.c, 1, 0, 0
        for h in range(self.B - 1, -1, -1):
            l = L[t]
            cl = c[l]
            if before + cl < k:
                before += cl
                t = R[t]
                v |= 1 << h
            else:
                t = l
        return v + self.lo, before, c[t]


    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max current
        self.n += c
        f = self._insert(x, c)  # x's new count
        n = self.n
        if c > 0:
            if n == c:  # the set was empty
                self.mn = self.mx = x
                return
            if x < self.mn:
                self.mn = x
            if x > self.mx:
                self.mx = x
        else:
            if not n:
                return
            if not f:  # x is gone: it may have been the min / max
                if x == self.mn:
                    self.mn = self._kth(1)
                if x == self.mx:
                    self.mx = self._kth(n)

    def _resetCached(self):  # nothing counted: as newly built
        self.n = self.d = 0

    def _clearData(self):  # just the empty node 0 and the root 1 (the old lists are freed in bulk)
        self.L = [0, 0]
        self.R = [0, 0]
        self.c = [0, 0]
        self.m = [1, 1]

    def _lcmIn(self, lo, hi):  # capped LCM of the values in [lo, hi]: the blocks that cover it, from the root down
        lo, hi = max(lo, self.lo) - self.lo, min(hi, self.hi) - self.lo
        if lo > hi:
            return 1
        L, R, f, res = self.L, self.R, self.m, 1
        stack = [(1, 0, self.B)]
        while stack:
            t, base, h = stack.pop()
            last = base + (1 << h) - 1
            if not t or last < lo or base > hi:
                continue
            if lo <= base and last <= hi:
                res = self._lc(res, f[t])
                continue
            h -= 1
            stack.append((L[t], base, h))
            stack.append((R[t], base + (1 << h), h))
        return res

    def _lcmLe(self, x):  # capped LCM of the values <= x
        return self._lcmIn(self.lo, x)

    def _lcmGe(self, x):  # capped LCM of the values >= x
        return self._lcmIn(x, self.hi)

    # O(logU * logU) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logU * logU) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1) -- LCM (-1 once it passes cap) of all values; 1 if empty
    def lcmOfAll(self):
        return self.m[1]

    # O(logU * logU) -- LCM (-1 once it passes cap) of the values > x; 1 if there are none
    def lcmOfGtX(self, x):
        return self._lcmGe(x + 1)

    # O(logU * logU) -- LCM (-1 once it passes cap) of the values >= x; 1 if there are none
    def lcmOfGteX(self, x):
        return self._lcmGe(x)

    # O(logU * logU) -- LCM (-1 once it passes cap) of the values v with lo <= v <= hi; 1 if there are none
    def lcmOfInValRange(self, lo, hi):
        return self._lcmIn(lo, hi) if lo <= hi else 1

    # O(logU * logU) -- LCM (-1 once it passes cap) of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and
    # inclusive: (1, 1) is
    # just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def lcmOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"lcmOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._lcmIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logU * logU) -- LCM (-1 once it passes cap) of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and
    # inclusive: (1, 1) is
    # just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError
    # unless 1 <= kFrom <= kTo <= size
    def lcmOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"lcmOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._lcmIn(self._kth(kFrom), self._kth(kTo))

    # O(logU * logU) -- LCM (-1 once it passes cap) of the k largest values; k is a COUNT, not an index: k = 0 takes no
    # values (returns 1),
    # k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    # raises IndexError unless 0 <= k <= size
    def lcmOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"lcmOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._lcmGe(self._kth(self.n - k + 1)) if k else 1

    # O(logU * logU) -- LCM (-1 once it passes cap) of the values < x; 1 if there are none
    def lcmOfLtX(self, x):
        return self._lcmLe(x - 1)

    # O(logU * logU) -- LCM (-1 once it passes cap) of the values <= x; 1 if there are none
    def lcmOfLteX(self, x):
        return self._lcmLe(x)

    # O(logU * logU) -- LCM (-1 once it passes cap) of the k smallest values; k is a COUNT, not an index: k = 0 takes no
    # values (returns 1),
    # k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
    # raises IndexError unless 0 <= k <= size
    def lcmOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"lcmOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._lcmLe(self._kth(k)) if k else 1

    # O(1 amortized) -- remove everything (fine on an empty set): afterwards it is as if newly built (same constructor
    # arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logU) -- how many copies of x (0 if x isn't there, e.g. on an empty set)
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values (0 if empty)
    def countDistinct(self):
        return self.d

    # O(logU) -- how many values > x (0 if there are none, e.g. on an empty set)
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(logU) -- how many values >= x (0 if there are none, e.g. on an empty set)
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(logU) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logU) -- how many values < x (0 if there are none, e.g. on an empty set)
    def countLtX(self, x):
        return self._lt(x)

    # O(logU) -- how many values <= x (0 if there are none, e.g. on an empty set)
    def countLteX(self, x):
        return self._le(x)

    # O(logU) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in
    # the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(logU) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    # kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); raises IndexError unless 0 <= i < size
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

    # O(logU) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is
    # not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(1) -- largest value; raises IndexError if empty
    def max(self):
        if not self.n:
            raise IndexError("max: the set is empty")
        return self.mx

    # O(logU) -- upper median: the (floor(size/2) + 1)-th smallest value; raises IndexError if empty
    def medianHigh(self):
        if not self.n:
            raise IndexError("medianHigh: the set is empty")
        return self._kth((self.n >> 1) + 1)

    # O(logU) -- lower median: the ceil(size/2)-th smallest value; raises IndexError if empty
    def medianLow(self):
        if not self.n:
            raise IndexError("medianLow: the set is empty")
        return self._kth((self.n + 1) >> 1)

    # O(1) -- smallest value; raises IndexError if empty
    def min(self):
        if not self.n:
            raise IndexError("min: the set is empty")
        return self.mn

    # O(logU * logU) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (=
    # popMin()),
    # pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logU * logU) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self.mx
        self._add(v, -1)
        return v

    # O(logU * logU) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self.mn
        self._add(v, -1)
        return v

    # O(logU * logU) -- remove one copy of x if present; returns how many were removed (0 or 1: 0 if x isn't there, e.g.
    # on an
    # empty set)
    def remove(self, x):
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logU * logU) -- remove every copy of val; returns how many were removed (0 if val isn't there, e.g. on an empty
    # set)
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logU * logU) -- remove min(cnt, count(val)) copies of val; returns how many were removed (0 if val isn't there,
    # e.g. on
    # an empty set)
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(logU * logU amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo
    # > hi)
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

    # O(1) -- how many values (copies count; 0 if empty)
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

    def _lc(self, a, b):  # capped LCM: 0 if either is 0, else -1 if either is -1 (too big), else the LCM or -1 past cap
        if a == 0 or b == 0:
            return 0
        if a < 0 or b < 0:
            return -1
        r = a // gcd(a, b) * b
        return r if r <= self.cap else -1

