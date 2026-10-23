# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/blocks-fenwick-with-sums/template.py
# @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow mex min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: blocks-fenwick
# @values: online
# @complexities:
#   add: sqrt(N)
#   addCount: sqrt(N)
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
#   popMax: sqrt(N)
#   popMin: sqrt(N)
#   remove: sqrt(N)
#   removeAll: sqrt(N)
#   removeCount: sqrt(N)
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
#   build: 1
# @memory:
#   layout: none
#   node: keys[1*N] cnts[1*N] fcs[1*N] sums[1*N] fss[1*N]
#   tags: none
#   other: maxes[1*sqrt(N)] bc[2*sqrt(N)] bs[2*sqrt(N)] cnt[1*N]
#   note: N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); queries are O(log N), and only updates that add or drop a distinct value pay O(sqrt N) (one block rebuilt)
from bisect import bisect_left, bisect_right
from itertools import accumulate
from operator import and_, sub


# Ordered multiset (online: any values, nothing known ahead), sqrt-style with a Fenwick tree inside every block: the
# distinct values in sorted blocks of LOAD..2*LOAD, each block keeping its values' copies and copies * value plus a Fenwick
# tree over them, and a Fenwick tree over the block totals. Every query is two Fenwick walks (over blocks, then inside
# one), so O(log N); an update that adds or drops a distinct value rebuilds its block's Fenwick (O(sqrt N), C-level).


class BlockFenwickMultiset:
    LOAD = 64
    __slots__ = ("keys", "cnts", "fcs", "sums", "fss", "maxes", "bc", "fc", "bs", "fs", "cnt", "n", "mn", "mx", "med", "lowV", "lowB", "lowC", "lowS", "highV", "highB", "highC", "mexV", "total", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.keys = []  # blocks of sorted distinct values
        self.cnts, self.fcs = [], []  # per block: copies of each value; Fenwick over them
        self.sums, self.fss = [], []  # per block: copies * value; Fenwick over them
        self.maxes = []  # last value of each block
        self.bc, self.fc = [], [0]  # per block: total copies; Fenwick over them
        self.bs, self.fs = [], [0]  # per block: total sum; Fenwick over them
        self.cnt = {}  # value -> copies
        self.med, self.mexV = False, -1  # medians / mex are tracked from their first query on; min / max always (set by the first add)
        self.n = self.total = self.d = 0

    @staticmethod
    def _build(a):  # Fenwick tree over a in C-level passes: f[i] = (prefix sum to i) - (prefix sum to i & (i - 1))
        p = list(accumulate(a, initial=0))
        m = len(p)
        return list(map(sub, p, map(p.__getitem__, map(and_, range(m), range(-1, m - 1)))))

    @staticmethod
    def _fen(f, i, v):
        i += 1
        while i < len(f):
            f[i] += v
            i += i & -i

    @staticmethod
    def _pre(f, i):  # f's total over positions 0..i-1
        res = 0
        while i > 0:
            res += f[i]
            i &= i - 1
        return res

    def _reblock(self):
        self.fc = self._build(self.bc)
        self.fs = self._build(self.bs)

    def _reinner(self, k):
        self.fcs[k] = self._build(self.cnts[k])
        self.fss[k] = self._build(self.sums[k])

    def _insert(self, x, c):
        old = self.cnt.get(x, 0)
        if old:
            k = bisect_left(self.maxes, x)
            j = bisect_left(self.keys[k], x)
            self.bc[k] += c
            self._fen(self.fc, k, c)
            self.bs[k] += c * x
            self._fen(self.fs, k, c * x)
            if old + c:  # x stays: point updates only
                self.cnt[x] = old + c
                self.cnts[k][j] += c
                self._fen(self.fcs[k], j, c)
                self.sums[k][j] += c * x
                self._fen(self.fss[k], j, c * x)
                return
            del self.cnt[x]
            self.d -= 1
            del self.keys[k][j], self.cnts[k][j]
            del self.sums[k][j]
            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.fcs[k], self.maxes[k], self.bc[k]
                del self.sums[k], self.fss[k], self.bs[k]
                self._reblock()
                return
            self.maxes[k] = self.keys[k][-1]
            self._reinner(k)
            return
        self.cnt[x] = c
        self.d += 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
            self.fcs.append(None)
            self.sums.append([c * x])
            self.fss.append(None)
            self.bs.append(c * x)
            self.maxes.append(x)
            self.bc.append(c)
            self._reinner(0)
            self._reblock()
            return
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            k -= 1
        j = bisect_left(self.keys[k], x)
        self.keys[k].insert(j, x)
        self.cnts[k].insert(j, c)
        self.sums[k].insert(j, c * x)
        self.bs[k] += c * x
        self._fen(self.fs, k, c * x)
        self.maxes[k] = self.keys[k][-1]
        self.bc[k] += c
        self._fen(self.fc, k, c)
        if len(self.keys[k]) > 2 * self.LOAD:  # split the block in half
            h = self.LOAD
            for arr in (self.keys, self.cnts, self.sums):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.fcs.insert(k + 1, None)
            self.fss.insert(k + 1, None)
            self._reinner(k)
            self._reinner(k + 1)
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
            self.bs[k:k + 1] = [sum(self.sums[k]), sum(self.sums[k + 1])]
            self._reblock()
        else:
            self._reinner(k)

    def _lt(self, x):
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.n
        return self._pre(self.fc, k) + self._pre(self.fcs[k], bisect_left(self.keys[k], x))

    def _le(self, x):
        k = bisect_right(self.maxes, x)  # the first block whose last value is > x
        if k == len(self.keys):
            return self.n
        return self._pre(self.fc, k) + self._pre(self.fcs[k], bisect_right(self.keys[k], x))

    def _slt(self, x):
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.total
        return self._pre(self.fs, k) + self._pre(self.fss[k], bisect_left(self.keys[k], x))

    def _sle(self, x):
        k = bisect_right(self.maxes, x)
        if k == len(self.keys):
            return self.total
        return self._pre(self.fs, k) + self._pre(self.fss[k], bisect_right(self.keys[k], x))

    def _countOf(self, x):
        return self.cnt.get(x, 0)

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies, sum before it): lift over blocks, then inside one
        fc, fs = self.fc, self.fs
        m = len(self.bc)
        b, before, acc = 0, 0, 0
        step = 1 << (m.bit_length() - 1)
        while step:
            nxt = b + step
            if nxt <= m and before + fc[nxt] < k:
                b = nxt
                before += fc[nxt]
                acc += fs[nxt]
            step >>= 1
        f, g = self.fcs[b], self.fss[b]
        m = len(self.keys[b])
        j = 0
        step = 1 << (m.bit_length() - 1)
        while step:
            nxt = j + step
            if nxt <= m and before + f[nxt] < k:
                j = nxt
                before += f[nxt]
                acc += g[nxt]
            step >>= 1
        return self.keys[b][j], before, self.cnts[b][j], acc

    def _kth(self, k):
        return self._kthInfo(k)[0]

    def _findMex(self):  # smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, ...
        keys = self.keys
        k = bisect_left(self.maxes, 0)
        if k == len(keys):
            return 0
        j = bisect_left(keys[k], 0)
        want = 0
        while k < len(keys):
            blk = keys[k]
            if blk[j] != want:
                return want
            if blk[-1] - blk[j] == len(blk) - 1 - j:  # this block continues the run to its end
                want = blk[-1] + 1
                k, j = k + 1, 0
                continue
            a, b = j, len(blk) - 1  # the run breaks inside: first p with blk[p] - p > blk[j] - j
            while a < b:
                mid = (a + b) // 2
                if blk[mid] - mid > blk[j] - j:
                    b = mid
                else:
                    a = mid + 1
            return blk[a - 1] + 1
        return want

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

    # O(sqrtN) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(sqrtN) -- add cnt copies of val (nothing if cnt <= 0)
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

    # O(sqrtN) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self.mx
        self._add(v, -1)
        return v

    # O(sqrtN) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self.mn
        self._add(v, -1)
        return v

    # O(sqrtN) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self.count(x):
            return 0
        self._add(x, -1)
        return 1

    # O(sqrtN) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(sqrtN) -- remove min(cnt, count(val)) copies of val; returns how many were removed
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
