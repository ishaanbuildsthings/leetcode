# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/fenwick-with-sums-mex/template.py
# @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow mex min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: fenwick
# @values: offline
# @complexities:
#   add: log(N)
#   addCount: log(N)
#   count: log(N)
#   countDistinct: 1
#   countGtX: log(N)
#   countGteX: log(N)
#   countInValRange: log(N)
#   countLtX: log(N)
#   countLteX: log(N)
#   kthLargest: log(N)
#   kthSmallest: log(N)
#   largestLtX: log(N)
#   largestLteX: log(N)
#   max: 1
#   medianHigh: 1 amortized
#   medianLow: 1 amortized
#   mex: 1 amortized
#   min: 1
#   popMax: log(N)
#   popMin: log(N)
#   remove: log(N)
#   removeAll: log(N)
#   removeCount: log(N)
#   size: 1
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   sumAbsDiffToMedian: 1 amortized
#   sumAbsDiffToX: log(N)
#   sumAll: 1
#   sumGtX: log(N)
#   sumGteX: log(N)
#   sumInValRange: log(N)
#   sumKthLargestRange: log(N)
#   sumKthSmallestRange: log(N)
#   sumLargestK: log(N)
#   sumLtX: log(N)
#   sumLteX: log(N)
#   sumSmallestK: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: cnt[1*N] fc[1*N] fp[1*N] fs[1*N]
#   tags: none
#   other: vals[1*N]
#   note: N = how many distinct values were given to the constructor; the arrays are allocated once
from bisect import bisect_left, bisect_right


# Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
# to the constructor, one counting copies, one summing them, one marking which values are present (for mex).
# k-th / sum of the k smallest walk down by binary lifting. The constructor only learns which values can appear (it
# compresses them); the multiset starts EMPTY. Every value you add must be one of them; query arguments (x, lo, hi)
# can be anything.


class FenwickMultiset:
    __slots__ = ("vals", "m", "top", "cnt", "fc", "fs", "fp", "z", "run", "n", "mn", "mx", "med", "lowV", "lowB", "lowC", "lowS", "highV", "highB", "highC", "mexV", "total", "d")

    # O(N log N) -- allValuesThatWillEverBeInsertedForOfflineCompression: every value you will EVER add (any order, duplicates fine), only to compress values; this does NOT add them, the multiset starts empty; N = distinct values
    def __init__(self, allValuesThatWillEverBeInsertedForOfflineCompression):
        vals = self.vals = sorted(set(allValuesThatWillEverBeInsertedForOfflineCompression))
        m = self.m = len(vals)
        self.top = 1 << (m.bit_length() - 1) if m else 0  # highest power of two <= m, for binary lifting
        self.cnt = [0] * m  # copies of vals[i]
        self.fc = [0] * (m + 1)  # Fenwick: copies
        self.fs = [0] * (m + 1)  # Fenwick: copies * value
        self.fp = [0] * (m + 1)  # Fenwick: 1 where the value is present
        z = self.z = bisect_left(vals, 0)
        run = 0
        while z + run < m and vals[z + run] == run:  # vals[z .. z + run - 1] = 0, 1, ..., run - 1
            run += 1
        self.run = run
        self.med, self.mexV = False, -1  # medians / mex are tracked from their first query on; min / max always (set by the first add)
        self.n = self.total = self.d = 0

    def _fen(self, f, i, v):
        m = self.m
        i += 1
        while i <= m:
            f[i] += v
            i += i & -i

    def _pre(self, f, i):  # f's total over positions 0..i-1
        s = 0
        while i > 0:
            s += f[i]
            i &= i - 1
        return s

    def _insert(self, x, c):
        i = bisect_left(self.vals, x)  # x must be one of the given values
        old = self.cnt[i]
        self.cnt[i] = old + c
        self._fen(self.fc, i, c)
        self._fen(self.fs, i, c * x)
        if not old:
            self._fen(self.fp, i, 1)
            self.d += 1
        elif not old + c:
            self._fen(self.fp, i, -1)
            self.d -= 1

    def _lt(self, x):
        return self._pre(self.fc, bisect_left(self.vals, x))

    def _le(self, x):
        return self._pre(self.fc, bisect_right(self.vals, x))

    def _countOf(self, x):
        i = bisect_left(self.vals, x)
        return self.cnt[i] if i < self.m and self.vals[i] == x else 0

    def _slt(self, x):
        return self._pre(self.fs, bisect_left(self.vals, x))

    def _sle(self, x):
        return self._pre(self.fs, bisect_right(self.vals, x))

    def _kth(self, k):  # binary lifting: the largest prefix with fewer than k copies ends right before the answer
        fc, m = self.fc, self.m
        pos, step = 0, self.top
        while step:
            nxt = pos + step
            if nxt <= m and fc[nxt] < k:
                pos = nxt
                k -= fc[nxt]
            step >>= 1
        return self.vals[pos]

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies, sum before it)
        fc, fs, m = self.fc, self.fs, self.m
        pos, step, before, acc = 0, self.top, 0, 0
        while step:
            nxt = pos + step
            if nxt <= m and before + fc[nxt] < k:
                pos = nxt
                before += fc[nxt]
                acc += fs[nxt]
            step >>= 1
        return self.vals[pos], before, self.cnt[pos], acc

    def _findMex(self):  # smallest non-negative integer not in the set
        if not self.run:
            return 0  # 0 is not even a possible value
        # first absent position p >= z: lift while the number of absent positions so far stays at the count before z
        fp, m, z = self.fp, self.m, self.z
        a0 = z - self._pre(fp, z)
        pos, step, acc = 0, self.top, 0
        while step:
            nxt = pos + step
            if nxt <= m and nxt - (acc + fp[nxt]) <= a0:
                pos = nxt
                acc += fp[nxt]
            step >>= 1
        return min(pos - z, self.run)

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max (and medians / mex once asked for) current
        self.n += c
        self.total += c * x
        self._insert(x, c)
        n = self.n
        if c > 0:
            if x == self.mexV and x >= 0:  # x filled the mex (mexV is -1 until mex() is first called)
                self.mexV = self._findMex()
            if n == c:  # the set was empty
                self.mn = self.mx = x
                if self.med:
                    self.lowV = self.highV = x
                    self.lowB = self.highB = self.lowS = 0
                    self.lowC = self.highC = c
                return
            if x < self.mn:
                self.mn = x
            if x > self.mx:
                self.mx = x
        else:
            if 0 <= x < self.mexV and not self._countOf(x):  # the last copy of a value below the mex
                self.mexV = x
            if not n:
                return
            if x == self.mn:
                self.mn = self._kth(1)
            if x == self.mx:
                self.mx = self._kth(n)
        if not self.med:
            return
        # each median is a tracked rank: shift its (value, copies before, copies, sum before), and search again only
        # when the rank leaves the tracked value
        if x < self.lowV:
            self.lowB += c
            self.lowS += c * x
        elif x == self.lowV:
            self.lowC += c
        r = (n + 1) >> 1
        if not self.lowB < r <= self.lowB + self.lowC:
            self.lowV, self.lowB, self.lowC, self.lowS = self._kthInfo(r)
        if x < self.highV:
            self.highB += c
        elif x == self.highV:
            self.highC += c
        r = (n >> 1) + 1
        if not self.highB < r <= self.highB + self.highC:
            self.highV, self.highB, self.highC = self._kthInfo(r)[:3]

    def _startMedians(self):  # the first median query (n > 0): from now on _add keeps both medians current
        self.med = True
        n = self.n
        self.lowV, self.lowB, self.lowC, self.lowS = self._kthInfo((n + 1) >> 1)
        self.highV, self.highB, self.highC = self._kthInfo((n >> 1) + 1)[:3]

    def _sumFirst(self, k):  # sum of the k smallest values
        if k <= 0:
            return 0
        v, b, _, s = self._kthInfo(k)
        return s + (k - b) * v

    # O(logN) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logN) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(logN) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(logN) -- how many values > x
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(logN) -- how many values >= x
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(logN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logN) -- how many values < x
    def countLtX(self, x):
        return self._lt(x)

    # O(logN) -- how many values <= x
    def countLteX(self, x):
        return self._le(x)

    # O(logN) -- k-th largest value (1-indexed); raises IndexError unless 1 <= k <= size
    def kthLargest(self, k):
        if not 1 <= k <= self.n:
            raise IndexError(f"kthLargest: needs 1 <= k <= size, got k = {k}, size = {self.n}")
        return self._kth(self.n - k + 1)

    # O(logN) -- k-th smallest value (1-indexed); raises IndexError unless 1 <= k <= size
    def kthSmallest(self, k):
        if not 1 <= k <= self.n:
            raise IndexError(f"kthSmallest: needs 1 <= k <= size, got k = {k}, size = {self.n}")
        return self._kth(k)

    # O(logN) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(logN) -- largest value <= x; None if there is none
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

    # O(1 amortized) -- smallest non-negative integer not in the set
    def mex(self):
        if self.mexV < 0:  # the first call: from now on _add keeps it current
            self.mexV = self._findMex()
        return self.mexV

    # O(1) -- smallest value; None if empty
    def min(self):
        return self.mn if self.n else None

    # O(logN) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self.mx
        self._add(v, -1)
        return v

    # O(logN) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self.mn
        self._add(v, -1)
        return v

    # O(logN) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self.count(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logN) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logN) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(1) -- how many values (copies count)
    def size(self):
        return self.n

    # O(logN) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logN) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None

    # O(1 amortized) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    def sumAbsDiffToMedian(self):
        if not self.n:
            return 0
        if not self.med:
            self._startMedians()
        v, b, c, s = self.lowV, self.lowB, self.lowC, self.lowS
        return v * b - s + (self.total - s - c * v) - v * (self.n - b - c)

    # O(logN) -- sum of |v - x| over all values
    def sumAbsDiffToX(self, x):
        c, s = self._lt(x), self._slt(x)
        return x * c - s + (self.total - s) - x * (self.n - c)

    # O(1) -- sum of all values
    def sumAll(self):
        return self.total

    # O(logN) -- sum of the values > x
    def sumGtX(self, x):
        return self.total - self._sle(x)

    # O(logN) -- sum of the values >= x
    def sumGteX(self, x):
        return self.total - self._slt(x)

    # O(logN) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    def sumInValRange(self, lo, hi):
        return self._sle(hi) - self._slt(lo) if lo <= hi else 0

    # O(logN) -- sum of the i-th..j-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); raises IndexError unless 1 <= i <= j <= size
    def sumKthLargestRange(self, i, j):
        if not 1 <= i <= j <= self.n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= i <= j <= size, got i = {i}, j = {j}, size = {self.n}")
        return self._sumFirst(self.n - i + 1) - self._sumFirst(self.n - j)

    # O(logN) -- sum of the i-th..j-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= i <= j <= size
    def sumKthSmallestRange(self, i, j):
        if not 1 <= i <= j <= self.n:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= i <= j <= size, got i = {i}, j = {j}, size = {self.n}")
        return self._sumFirst(j) - self._sumFirst(i - 1)

    # O(logN) -- sum of the k largest values; raises IndexError unless 0 <= k <= size
    def sumLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.total - self._sumFirst(self.n - k)

    # O(logN) -- sum of the values < x
    def sumLtX(self, x):
        return self._slt(x)

    # O(logN) -- sum of the values <= x
    def sumLteX(self, x):
        return self._sle(x)

    # O(logN) -- sum of the k smallest values; raises IndexError unless 0 <= k <= size
    def sumSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._sumFirst(k)
