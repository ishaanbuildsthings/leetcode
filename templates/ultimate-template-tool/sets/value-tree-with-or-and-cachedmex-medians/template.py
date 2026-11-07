# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/value-tree-with-or-and-cachedmex-medians/template.py
# @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
# @data-structure-type: value-tree
# @values: online-range
# @keys: numbers
# @tracks: medians mex
# @complexities:
#   add: log(U)
#   addCount: log(U)
#   andOfAll: 1
#   andOfGtX: log(U)
#   andOfGteX: log(U)
#   andOfInValRange: log(U)
#   andOfKthLargestRange: log(U)
#   andOfKthSmallestRange: log(U)
#   andOfLargestK: log(U)
#   andOfLtX: log(U)
#   andOfLteX: log(U)
#   andOfSmallestK: log(U)
#   clear: 1 amortized
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
#   medianHigh: 1
#   medianLow: 1
#   mex: 1
#   min: log(U)
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
#   build: 1
# @memory:
#   layout: sparse
#   node: c[1*log(U)] p[1*log(U)] o[1*log(U)] a[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per add of a new value, one node per level of its root path; U = hi - lo + 1. C++: each multiset owns its node pool (node 0 = empty); Python: dicts keyed by heap index

# Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
# each node keeping how many copies, their OR, their AND and how many distinct values (for mex) are below it. Sparse: dicts keyed by heap
# index over a power-of-two cover of [lo, hi]; a missing key is an empty block. k-th / sums of the k smallest descend
# by counts; mex descends to the first value >= 0 whose block isn't full.


class ValueTreeMultiset:
    __slots__ = ("lo", "hi", "B", "L", "R", "c", "o", "a", "p", "n", "lowV", "lowB", "lowC", "highV", "highB", "highC", "mexV", "d")

    # O(1) -- an empty multiset for values in [lo, hi] (any integers, negative is fine)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.B = (hi - lo).bit_length()  # levels below the root: a value's path is the bits of v - lo, highest first
        self._clearData()
        self.mexV = 0  # the mex, kept current (0 for the empty set)
        self.n = self.d = 0

    def _newNode(self):
        self.L.append(0)
        self.R.append(0)
        self.c.append(0)
        self.p.append(0)
        self.o.append(0)
        self.a.append(-1)
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
        if pres:
            pp = self.p
            for i in path:
                pp[i] += pres
        if pres:  # x appeared or disappeared: the OR / AND up its path, each node from its two children
            oo = self.o
            aa = self.a
            oo[t] = x if old + c > 0 else 0
            aa[t] = x if old + c > 0 else -1
            for i in reversed(path[:-1]):
                oo[i] = oo[L[i]] | oo[R[i]]
                aa[i] = aa[L[i]] & aa[R[i]]
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

    # smallest non-negative integer not in the set (hi + 1 if all of [0, hi] are present)
    def _findMex(self):
        if self.lo > 0:
            return 0
        if self.hi < 0:
            return self.hi + 1
        L, R, p, off, t = self.L, self.R, self.p, -self.lo, 1
        later = []  # blocks right of the path to 0, nearest last: (node, its first value, levels below it)
        for h in range(self.B - 1, -1, -1):
            if off >> h & 1:
                t = R[t]
            else:
                later.append((R[t], (off >> h | 1) << h, h))
                t = L[t]
            if not t:
                return 0
        if not p[t]:
            return 0
        while later:
            t, base, h = later.pop()
            if p[t] == 1 << h:
                continue
            while t and h:  # the first missing value is inside: descend, preferring the left child
                h -= 1
                l = L[t]
                if p[l] == 1 << h:
                    base += 1 << h
                    t = R[t]
                else:
                    t = l
            return min(base + self.lo, self.hi + 1)
        return self.hi + 1

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps both medians, the mex current
        self.n += c
        f = self._insert(x, c)  # x's new count
        n = self.n
        if c > 0:
            if x == self.mexV:  # x filled the mex
                self.mexV = self._findMex()
            if n == c:  # the set was empty
                self.lowV = self.highV = x
                self.lowB = self.highB = 0
                self.lowC = self.highC = c
                return
        else:
            if 0 <= x < self.mexV and not f:  # the last copy of a value below the mex
                self.mexV = x
            if not n:
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

    def _resetCached(self):  # nothing counted: as newly built
        self.mexV = 0
        self.n = self.d = 0

    def _clearData(self):  # just the empty node 0 and the root 1 (the old lists are freed in bulk)
        self.L = [0, 0]
        self.R = [0, 0]
        self.c = [0, 0]
        self.p = [0, 0]
        self.o = [0, 0]
        self.a = [-1, -1]

    def _distinctLt(self, x):  # distinct values < x
        return self._prefix(self.p, x)

    def _orIn(self, lo, hi):  # OR of the values in [lo, hi]: the blocks that cover it, from the root down
        lo, hi = max(lo, self.lo) - self.lo, min(hi, self.hi) - self.lo
        if lo > hi:
            return 0
        L, R, f, res = self.L, self.R, self.o, 0
        stack = [(1, 0, self.B)]
        while stack:
            t, base, h = stack.pop()
            last = base + (1 << h) - 1
            if not t or last < lo or base > hi:
                continue
            if lo <= base and last <= hi:
                res |= f[t]
                continue
            h -= 1
            stack.append((L[t], base, h))
            stack.append((R[t], base + (1 << h), h))
        return res

    def _orLe(self, x):  # OR of the values <= x
        return self._orIn(self.lo, x)

    def _orGe(self, x):  # OR of the values >= x
        return self._orIn(x, self.hi)

    def _andIn(self, lo, hi):  # AND of the values in [lo, hi]: the blocks that cover it, from the root down
        lo, hi = max(lo, self.lo) - self.lo, min(hi, self.hi) - self.lo
        if lo > hi:
            return -1
        L, R, f, res = self.L, self.R, self.a, -1
        stack = [(1, 0, self.B)]
        while stack:
            t, base, h = stack.pop()
            last = base + (1 << h) - 1
            if not t or last < lo or base > hi:
                continue
            if lo <= base and last <= hi:
                res &= f[t]
                continue
            h -= 1
            stack.append((L[t], base, h))
            stack.append((R[t], base + (1 << h), h))
        return res

    def _andLe(self, x):  # AND of the values <= x
        return self._andIn(self.lo, x)

    def _andGe(self, x):  # AND of the values >= x
        return self._andIn(x, self.hi)

    # O(logU) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logU) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1) -- bitwise AND of all values; -1 (every bit set) if empty
    def andOfAll(self):
        return self.a[1]

    # O(logU) -- bitwise AND of the values > x; -1 (every bit set) if there are none
    def andOfGtX(self, x):
        return self._andGe(x + 1)

    # O(logU) -- bitwise AND of the values >= x; -1 (every bit set) if there are none
    def andOfGteX(self, x):
        return self._andGe(x)

    # O(logU) -- bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none
    def andOfInValRange(self, lo, hi):
        return self._andIn(lo, hi) if lo <= hi else -1

    # O(logU) -- bitwise AND of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def andOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"andOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._andIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logU) -- bitwise AND of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError
    # unless 1 <= kFrom <= kTo <= size
    def andOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"andOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._andIn(self._kth(kFrom), self._kth(kTo))

    # O(logU) -- bitwise AND of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns -1,
    # every bit set), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    # raises IndexError unless 0 <= k <= size
    def andOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"andOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._andGe(self._kth(self.n - k + 1)) if k else -1

    # O(logU) -- bitwise AND of the values < x; -1 (every bit set) if there are none
    def andOfLtX(self, x):
        return self._andLe(x - 1)

    # O(logU) -- bitwise AND of the values <= x; -1 (every bit set) if there are none
    def andOfLteX(self, x):
        return self._andLe(x)

    # O(logU) -- bitwise AND of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns -1,
    # every bit set), k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
    # raises IndexError unless 0 <= k <= size
    def andOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"andOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._andLe(self._kth(k)) if k else -1

    # O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    # instead of building a new one
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

    # O(logU) -- largest value; raises IndexError if empty
    def max(self):
        if not self.n:
            raise IndexError("max: the set is empty")
        return self._kth(self.n)

    # O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; raises IndexError if empty
    def medianHigh(self):
        if not self.n:
            raise IndexError("medianHigh: the set is empty")
        return self.highV

    # O(1) -- lower median: the ceil(size/2)-th smallest value; raises IndexError if empty
    def medianLow(self):
        if not self.n:
            raise IndexError("medianLow: the set is empty")
        return self.lowV

    # O(1) -- smallest non-negative integer not in the set
    def mex(self):
        return self.mexV

    # O(logU) -- smallest value; raises IndexError if empty
    def min(self):
        if not self.n:
            raise IndexError("min: the set is empty")
        return self._kth(1)

    # O(1) -- bitwise OR of all values; 0 if empty
    def orOfAll(self):
        return self.o[1]

    # O(logU) -- bitwise OR of the values > x; 0 if there are none
    def orOfGtX(self, x):
        return self._orGe(x + 1)

    # O(logU) -- bitwise OR of the values >= x; 0 if there are none
    def orOfGteX(self, x):
        return self._orGe(x)

    # O(logU) -- bitwise OR of the values v with lo <= v <= hi; 0 if there are none
    def orOfInValRange(self, lo, hi):
        return self._orIn(lo, hi) if lo <= hi else 0

    # O(logU) -- bitwise OR of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._orIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logU) -- bitwise OR of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError
    # unless 1 <= kFrom <= kTo <= size
    def orOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._orIn(self._kth(kFrom), self._kth(kTo))

    # O(logU) -- bitwise OR of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k =
    # 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); raises IndexError
    # unless 0 <= k <= size
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

    # O(logU) -- bitwise OR of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k =
    # 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); raises IndexError
    # unless 0 <= k <= size
    def orOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orLe(self._kth(k)) if k else 0

    # O(logU) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (= popMin()),
    # pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logU) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(logU) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self._kth(1)
        self._add(v, -1)
        return v

    # O(logU) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self._countOf(x):
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
