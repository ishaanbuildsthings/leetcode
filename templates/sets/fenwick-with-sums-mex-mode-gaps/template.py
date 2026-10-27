# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/fenwick-with-sums-mex-mode-gaps/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff mode pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: fenwick
# @values: offline
# @keys: numbers
# @tracks: mode gaps
# @complexities:
#   add: log(N)
#   addCount: log(N)
#   clear: N
#   count: log(N)
#   countDistinct: 1
#   countDistinctInValRange: log(N)
#   countGtX: log(N)
#   countGteX: log(N)
#   countInValRange: log(N)
#   countLtX: log(N)
#   countLteX: log(N)
#   firstIndex: log(N)
#   kth: log(N)
#   largestLtX: log(N)
#   largestLteX: log(N)
#   lastIndex: log(N)
#   max: log(N)
#   maxGap: 1 amortized
#   medianHigh: log(N)
#   medianLow: log(N)
#   mex: log(N)
#   min: log(N)
#   minAdjacentDiff: 1 amortized
#   mode: 1
#   pop: log(N)
#   popMax: log(N)
#   popMin: log(N)
#   remove: log(N)
#   removeAll: log(N)
#   removeCount: log(N)
#   removeInValRange: log(N) amortized
#   size: 1
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   sumAbsDiffToMedian: log(N)
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
from heapq import heappop, heappush
from bisect import bisect_left, bisect_right


# Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
# to the constructor, one counting copies, one summing them, one marking which values are present (for mex).
# k-th / sum of the k smallest walk down by binary lifting. The constructor only learns which values can appear (it
# compresses them); the multiset starts EMPTY. Every value you add must be one of them; query arguments (x, lo, hi)
# can be anything.


class FenwickMultiset:
    __slots__ = ("vals", "m", "top", "cnt", "fc", "fs", "fp", "z", "run", "n", "bk", "maxF", "gc", "gmin", "gmax", "dups", "total", "d")

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
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.bk, self.maxF = {}, 0  # mode: count -> the values with that many copies; the highest count
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
        return old + c  # (x's new count)

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
        if (g >= 2) != (f >= 2):  # values with 2+ copies (then the smallest difference is 0)
            self.dups += 1 if f >= 2 else -1
        if not g or not f:  # x appeared or disappeared: the gap between its neighbours splits or comes back
            p, q = self.largestLtX(x), self.smallestGtX(x)
            if f:
                if p is not None and q is not None:
                    self._gap(q - p, -1)
                if p is not None:
                    self._gap(x - p, 1)
                if q is not None:
                    self._gap(q - x, 1)
            else:
                if p is not None:
                    self._gap(x - p, -1)
                if q is not None:
                    self._gap(q - x, -1)
                if p is not None and q is not None:
                    self._gap(q - p, 1)

    def _gap(self, g, c):  # one more (c = 1) / fewer (c = -1) gap of size g
        gc = self.gc
        k = gc.get(g, 0) + c
        if k:
            gc[g] = k
            if k == 1 and c > 0:  # (a size already present has an entry in both heaps)
                if len(self.gmin) > 2 * len(gc) + 8:  # mostly sizes no longer present: rebuild from the live ones
                    self.gmin = sorted(gc)
                    self.gmax = [-v for v in reversed(self.gmin)]
                else:
                    heappush(self.gmin, g)
                    heappush(self.gmax, -g)
        else:
            del gc[g]

    def _minGap(self):  # heap tops of sizes no longer present are dropped as they surface
        h, gc = self.gmin, self.gc
        while h[0] not in gc:
            heappop(h)
        return h[0]

    def _maxGap(self):
        h, gc = self.gmax, self.gc
        while -h[0] not in gc:
            heappop(h)
        return -h[0]

    def _sumFirst(self, k):  # sum of the k smallest values
        if k <= 0:
            return 0
        v, b, _, s = self._kthInfo(k)
        return s + (k - b) * v

    def _resetCached(self):  # nothing counted: as newly built
        self.bk, self.maxF = {}, 0
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0
        self.n = self.d = 0
        self.total = 0

    def _clearData(self):  # few distinct values present: zero only their slots and Fenwick paths, else wipe in bulk
        m, fc, cnt = self.m, self.fc, self.cnt
        if self.d * (self.top.bit_length() + 1) * 8 < m:
            fs, fp = self.fs, self.fp
            slots, k = [], 1
            while k <= self.n:  # the slot of the k-th smallest, by binary lifting; then skip its copies
                pos, step, before = 0, self.top, 0
                while step:
                    nxt = pos + step
                    if nxt <= m and before + fc[nxt] < k:
                        pos, before = nxt, before + fc[nxt]
                    step >>= 1
                slots.append(pos)
                k = before + cnt[pos] + 1
            for i in slots:
                cnt[i] = 0
                j = i + 1
                while j <= m:
                    fc[j] = 0
                    fs[j] = 0
                    fp[j] = 0
                    j += j & -j
        else:
            self.cnt = [0] * m
            self.fc = [0] * (m + 1)
            self.fs = [0] * (m + 1)
            self.fp = [0] * (m + 1)

    def _distinctLt(self, x):  # distinct values < x: the Fenwick of present values
        return self._pre(self.fp, bisect_left(self.vals, x))

    # O(logN) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logN) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logN) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(logN) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    def countDistinctInValRange(self, lo, hi):
        if lo > hi:
            return 0
        return self._distinctLt(hi) - self._distinctLt(lo) + (1 if self._countOf(hi) else 0)

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

    # O(logN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(logN) -- the value at sorted position i (0-indexed: kth(0) is the min); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1)

    # O(logN) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(logN) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        c = self._le(x)
        return self._kth(c) if c else None

    # O(logN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(logN) -- largest value; None if empty
    def max(self):
        return self._kth(self.n) if self.n else None

    # O(1 amortized) -- largest difference between two neighbouring distinct values; None if fewer than 2 distinct values
    def maxGap(self):
        return self._maxGap() if self.d >= 2 else None

    # O(logN) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        return self._kth((self.n >> 1) + 1) if self.n else None

    # O(logN) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        return self._kth((self.n + 1) >> 1) if self.n else None

    # O(logN) -- smallest non-negative integer not in the set
    def mex(self):
        return self._findMex()

    # O(logN) -- smallest value; None if empty
    def min(self):
        return self._kth(1) if self.n else None

    # O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); None if fewer than 2 values
    def minAdjacentDiff(self):
        if self.n < 2:
            return None
        return 0 if self.dups else self._minGap()

    # O(1) -- (a most frequent value, its count); None if empty. C++ returns the smallest of the most frequent values
    def mode(self):
        if not self.n:
            return None
        f = self.maxF
        return next(iter(self.bk[f])), f

    # O(logN) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logN) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(logN) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self._kth(1)
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

    # O(logN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    # O(logN) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logN) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logN) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    def sumAbsDiffToMedian(self):
        if not self.n:
            return 0
        v, b, c, s = self._kthInfo((self.n + 1) >> 1)
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

    # O(logN) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); raises IndexError unless 1 <= kFrom <= kTo <= size
    def sumKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._sumFirst(self.n - kFrom + 1) - self._sumFirst(self.n - kTo)

    # O(logN) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def sumKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._sumFirst(kTo) - self._sumFirst(kFrom - 1)

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
