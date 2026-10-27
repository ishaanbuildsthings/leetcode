# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/blocks-with-sums-minmax-mode-gaps-shift/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff mode pop popMax popMin remove removeAll removeCount removeInValRange shiftAll size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: blocks
# @values: online
# @keys: numbers
# @tracks: minmax mode gaps shift
# @complexities:
#   add: sqrt(N)
#   addCount: sqrt(N)
#   clear: N
#   count: log(N)
#   countDistinct: 1
#   countDistinctInValRange: sqrt(N)
#   countGtX: sqrt(N)
#   countGteX: sqrt(N)
#   countInValRange: sqrt(N)
#   countLtX: sqrt(N)
#   countLteX: sqrt(N)
#   firstIndex: sqrt(N)
#   kth: sqrt(N)
#   largestLtX: sqrt(N)
#   largestLteX: sqrt(N)
#   lastIndex: sqrt(N)
#   max: 1
#   maxGap: 1 amortized
#   medianHigh: sqrt(N)
#   medianLow: sqrt(N)
#   mex: sqrt(N)
#   min: 1
#   minAdjacentDiff: 1 amortized
#   mode: 1
#   pop: sqrt(N)
#   popMax: sqrt(N)
#   popMin: sqrt(N)
#   remove: sqrt(N)
#   removeAll: sqrt(N)
#   removeCount: sqrt(N)
#   removeInValRange: sqrt(N) amortized
#   shiftAll: 1
#   size: 1
#   smallestGtX: sqrt(N)
#   smallestGteX: sqrt(N)
#   sumAbsDiffToMedian: sqrt(N)
#   sumAbsDiffToX: sqrt(N)
#   sumAll: 1
#   sumGtX: sqrt(N)
#   sumGteX: sqrt(N)
#   sumInValRange: sqrt(N)
#   sumKthLargestRange: sqrt(N)
#   sumKthSmallestRange: sqrt(N)
#   sumLargestK: sqrt(N)
#   sumLtX: sqrt(N)
#   sumLteX: sqrt(N)
#   sumSmallestK: sqrt(N)
#   build: 1
# @memory:
#   layout: none
#   node: keys[1*N] cnts[1*N] sums[1*N]
#   tags: none
#   other: maxes[1*sqrt(N)] bc[2*sqrt(N)] bs[2*sqrt(N)] cnt[1*N]
#   note: N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); each operation costs a few binary searches plus one block's worth of C-level list work
from heapq import heappop, heappush
from bisect import bisect_left, bisect_right, insort
from itertools import accumulate


# Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
# LOAD..2*LOAD, each block keeping its values' copies and copies * value plus block totals, and a Fenwick tree over the
# block totals (rebuilt only after a block splits or empties). A query finds its block by binary search (or by
# lifting over the block Fenwick for k-th) and then works inside one block with C-level list operations.


class BlockMultiset:
    LOAD = 64
    __slots__ = ("keys", "cnts", "sums", "maxes", "bc", "bs", "fc", "fs", "cnt", "n", "mn", "mx", "bk", "maxF", "gc", "gmin", "gmax", "dups", "off", "total", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.keys = []  # blocks of sorted distinct values
        self.cnts = []  # per block: copies of each value
        self.sums = []  # per block: copies * value
        self.maxes = []  # last value of each block
        self.bc = []  # per block: total copies
        self.bs = []  # per block: total sum
        self.fc = None  # Fenwick over bc (None: stale)
        self.fs = None  # Fenwick over bs (None: stale)
        self.cnt = {}  # value -> copies
        self.off = 0  # every value v is stored as v - off: shiftAll only moves off
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.bk, self.maxF = {}, 0  # mode: count -> the values with that many copies; the highest count
        self.n = self.total = self.d = 0

    @staticmethod
    def _build(a):
        f = [0] + a
        for i in range(1, len(f)):
            j = i + (i & -i)
            if j < len(f):
                f[j] += f[i]
        return f

    @staticmethod
    def _fen(f, i, v):
        if f is not None:
            i += 1
            while i < len(f):
                f[i] += v
                i += i & -i

    def _pre(self, which, k):  # total of blocks 0..k-1
        f = self.fc if which == 0 else self.fs
        if f is None:
            f = self._build(self.bc if which == 0 else self.bs)
            if which == 0:
                self.fc = f
            else:
                self.fs = f
        res = 0
        while k > 0:
            res += f[k]
            k &= k - 1
        return res

    def _insert(self, x, c):
        old = self.cnt.get(x, 0)
        if old:
            k = bisect_left(self.maxes, x)
            j = bisect_left(self.keys[k], x)
            if old + c:
                self.cnt[x] = old + c
                self.cnts[k][j] += c
                self.sums[k][j] += c * x
                self.bc[k] += c
                self._fen(self.fc, k, c)
                self.bs[k] += c * x
                self._fen(self.fs, k, c * x)
                return old + c
            del self.cnt[x]
            self.d -= 1
            del self.keys[k][j], self.cnts[k][j]
            del self.sums[k][j]
            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.maxes[k], self.bc[k]
                del self.sums[k], self.bs[k]
                self.fc = self.fs = None
                return 0
            self.maxes[k] = self.keys[k][-1]
            self.bc[k] += c
            self._fen(self.fc, k, c)
            self.bs[k] += c * x
            self._fen(self.fs, k, c * x)
            return 0
        self.cnt[x] = c
        self.d += 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
            self.sums.append([c * x])
            self.maxes.append(x)
            self.bc.append(c)
            self.bs.append(c * x)
            self.fc = self.fs = None
            return c
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            k -= 1
        j = bisect_left(self.keys[k], x)
        self.keys[k].insert(j, x)
        self.cnts[k].insert(j, c)
        self.sums[k].insert(j, c * x)
        self.maxes[k] = self.keys[k][-1]
        self.bc[k] += c
        self._fen(self.fc, k, c)
        self.bs[k] += c * x
        self._fen(self.fs, k, c * x)
        if len(self.keys[k]) > 2 * self.LOAD:  # split the block in half
            h = self.LOAD
            for arr in (self.keys, self.cnts, self.sums):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
            self.bs[k:k + 1] = [sum(self.sums[k]), sum(self.sums[k + 1])]
            self.fc = self.fs = None
        return c

    def _count(self, x, strict, which):  # copies (which=0) or sums (which=1) of the values < x (strict) or <= x
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.n if which == 0 else self.total
        j = (bisect_left if strict else bisect_right)(self.keys[k], x)
        return self._pre(which, k) + sum((self.cnts if which == 0 else self.sums)[k][:j])

    def _lt(self, x):
        return self._count(x, True, 0)

    def _le(self, x):
        return self._count(x, False, 0)

    def _countOf(self, x):
        return self.cnt.get(x, 0)

    def _slt(self, x):
        return self._count(x, True, 1)

    def _sle(self, x):
        return self._count(x, False, 1)

    def _locate(self, k):  # (block, copies before it, sum before it) for the block holding the k-th smallest
        self._pre(0, 0)
        self._pre(1, 0)
        fc, fs = self.fc, self.fs
        pos, before, acc = 0, 0, 0
        step = 1 << (len(self.bc).bit_length() - 1) if self.bc else 0
        while step:
            nxt = pos + step
            if nxt <= len(self.bc) and before + fc[nxt] < k:
                pos = nxt
                before += fc[nxt]
                acc += fs[nxt]
            step >>= 1
        return pos, before, acc

    def _kth(self, k):
        b, before, _ = self._locate(k)
        return self.keys[b][bisect_left(list(accumulate(self.cnts[b])), k - before)]
    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies, sum before it)
        b, before, acc = self._locate(k)
        cn = self.cnts[b]
        pre = list(accumulate(cn))
        j = bisect_left(pre, k - before)
        return self.keys[b][j], before + pre[j] - cn[j], cn[j], acc + sum(self.sums[b][:j])
    # smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, 2, ...
    def _findMex(self):
        keys = self.keys
        base = -self.off  # (stored as v - off: the real values >= 0 are the stored ones >= -off)
        k = bisect_left(self.maxes, base)
        if k == len(keys):
            return base
        j = bisect_left(keys[k], base)
        want = base
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

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max current
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
            i, j = self._lt(x), self._le(x)  # (stored values: the public ops would shift x again)
            p, q = self._kth(i) if i else None, self._kth(j + 1) if j < self.n else None
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
        self.off = 0

    def _clearData(self):
        self.keys, self.cnts, self.maxes, self.bc = [], [], [], []
        self.fc = None
        self.cnt = {}
        self.sums, self.bs = [], []
        self.fs = None

    def _distinctLt(self, x):  # distinct values < x: every block before x's, then a binary search in x's block
        keys = self.keys
        b = bisect_left(self.maxes, x)
        return sum(map(len, keys[:b])) + (bisect_left(keys[b], x) if b < len(keys) else 0)

    # O(sqrtN) -- add one copy of x
    def add(self, x):
        x -= self.off
        self._add(x, 1)

    # O(sqrtN) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        val -= self.off
        if cnt > 0:
            self._add(val, cnt)

    # O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logN) -- how many copies of x
    def count(self, x):
        x -= self.off
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(sqrtN) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    def countDistinctInValRange(self, lo, hi):
        lo -= self.off
        hi -= self.off
        if lo > hi:
            return 0
        return self._distinctLt(hi) - self._distinctLt(lo) + (1 if self._countOf(hi) else 0)

    # O(sqrtN) -- how many values > x
    def countGtX(self, x):
        x -= self.off
        return self.n - self._le(x)

    # O(sqrtN) -- how many values >= x
    def countGteX(self, x):
        x -= self.off
        return self.n - self._lt(x)

    # O(sqrtN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        lo -= self.off
        hi -= self.off
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(sqrtN) -- how many values < x
    def countLtX(self, x):
        x -= self.off
        return self._lt(x)

    # O(sqrtN) -- how many values <= x
    def countLteX(self, x):
        x -= self.off
        return self._le(x)

    # O(sqrtN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    def firstIndex(self, x):
        x -= self.off
        return self._lt(x) if self._countOf(x) else -1

    # O(sqrtN) -- the value at sorted position i (0-indexed: kth(0) is the min); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1) + self.off

    # O(sqrtN) -- largest value < x; None if there is none
    def largestLtX(self, x):
        x -= self.off
        c = self._lt(x)
        return self._kth(c) + self.off if c else None

    # O(sqrtN) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        x -= self.off
        c = self._le(x)
        return self._kth(c) + self.off if c else None

    # O(sqrtN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    def lastIndex(self, x):
        x -= self.off
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(1) -- largest value; None if empty
    def max(self):
        return self.mx + self.off if self.n else None

    # O(1 amortized) -- largest difference between two neighbouring distinct values; None if fewer than 2 distinct values
    def maxGap(self):
        return self._maxGap() if self.d >= 2 else None

    # O(sqrtN) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        return self._kth((self.n >> 1) + 1) + self.off if self.n else None

    # O(sqrtN) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        return self._kth((self.n + 1) >> 1) + self.off if self.n else None

    # O(sqrtN) -- smallest non-negative integer not in the set
    def mex(self):
        return self._findMex() + self.off

    # O(1) -- smallest value; None if empty
    def min(self):
        return self.mn + self.off if self.n else None

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
        return next(iter(self.bk[f])) + self.off, f

    # O(sqrtN) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v + self.off

    # O(sqrtN) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self.mx
        self._add(v, -1)
        return v + self.off

    # O(sqrtN) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self.mn
        self._add(v, -1)
        return v + self.off

    # O(sqrtN) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        x -= self.off
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(sqrtN) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        val -= self.off
        k = self._countOf(val)
        if k:
            self._add(val, -k)
        return k

    # O(sqrtN) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        val -= self.off
        k = min(cnt, self._countOf(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(sqrtN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    def removeInValRange(self, lo, hi):
        lo -= self.off
        hi -= self.off
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

    # O(1) -- add d to every value (d may be negative)
    def shiftAll(self, d):
        self.off += d

    # O(1) -- how many values (copies count)
    def size(self):
        return self.n

    # O(1) -- same as size()
    def __len__(self):
        return self.n

    # O(sqrtN) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        x -= self.off
        c = self._le(x)
        return self._kth(c + 1) + self.off if c < self.n else None

    # O(sqrtN) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        x -= self.off
        c = self._lt(x)
        return self._kth(c + 1) + self.off if c < self.n else None

    # O(sqrtN) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    def sumAbsDiffToMedian(self):
        if not self.n:
            return 0
        v, b, c, s = self._kthInfo((self.n + 1) >> 1)
        return v * b - s + (self.total - s - c * v) - v * (self.n - b - c)

    # O(sqrtN) -- sum of |v - x| over all values
    def sumAbsDiffToX(self, x):
        x -= self.off
        c, s = self._lt(x), self._slt(x)
        return x * c - s + (self.total - s) - x * (self.n - c)

    # O(1) -- sum of all values
    def sumAll(self):
        return self.total + self.off * self.n

    # O(sqrtN) -- sum of the values > x
    def sumGtX(self, x):
        x -= self.off
        return self.total - self._sle(x) + self.off * (self.n - self._le(x))

    # O(sqrtN) -- sum of the values >= x
    def sumGteX(self, x):
        x -= self.off
        return self.total - self._slt(x) + self.off * (self.n - self._lt(x))

    # O(sqrtN) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    def sumInValRange(self, lo, hi):
        if lo > hi:
            return 0
        lo -= self.off
        hi -= self.off
        return self._sle(hi) - self._slt(lo) + self.off * (self._le(hi) - self._lt(lo))

    # O(sqrtN) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); raises IndexError unless 1 <= kFrom <= kTo <= size
    def sumKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._sumFirst(self.n - kFrom + 1) - self._sumFirst(self.n - kTo) + self.off * (kTo - kFrom + 1)

    # O(sqrtN) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def sumKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._sumFirst(kTo) - self._sumFirst(kFrom - 1) + self.off * (kTo - kFrom + 1)

    # O(sqrtN) -- sum of the k largest values; raises IndexError unless 0 <= k <= size
    def sumLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.total - self._sumFirst(self.n - k) + self.off * k

    # O(sqrtN) -- sum of the values < x
    def sumLtX(self, x):
        x -= self.off
        return self._slt(x) + self.off * self._lt(x)

    # O(sqrtN) -- sum of the values <= x
    def sumLteX(self, x):
        x -= self.off
        return self._sle(x) + self.off * self._le(x)

    # O(sqrtN) -- sum of the k smallest values; raises IndexError unless 0 <= k <= size
    def sumSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._sumFirst(k) + self.off * k
