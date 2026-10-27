# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/blocks-fenwick-with-sums-xor-cachedmex-medians/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
# @data-structure-type: blocks-fenwick
# @values: online
# @keys: numbers
# @tracks: medians mex
# @complexities:
#   add: sqrt(N)
#   addCount: sqrt(N)
#   clear: N
#   count: log(N)
#   countDistinct: 1
#   countDistinctInValRange: sqrt(N)
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
#   medianHigh: 1
#   medianLow: 1
#   mex: 1
#   min: log(N)
#   pop: sqrt(N)
#   popMax: sqrt(N)
#   popMin: sqrt(N)
#   remove: sqrt(N)
#   removeAll: sqrt(N)
#   removeCount: sqrt(N)
#   removeInValRange: sqrt(N) amortized
#   size: 1
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   sumAbsDiffToMedian: 1
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
#   xorOfAll: 1
#   xorOfGtX: log(N)
#   xorOfGteX: log(N)
#   xorOfInValRange: log(N)
#   xorOfKthLargestRange: log(N)
#   xorOfKthSmallestRange: log(N)
#   xorOfLargestK: log(N)
#   xorOfLtX: log(N)
#   xorOfLteX: log(N)
#   xorOfSmallestK: log(N)
#   build: 1
# @memory:
#   layout: none
#   node: keys[1*N] cnts[1*N] fcs[1*N] sums[1*N] fss[1*N] xvs[1*N] fxs[1*N]
#   tags: none
#   other: maxes[1*sqrt(N)] bc[2*sqrt(N)] bs[2*sqrt(N)] bx[2*sqrt(N)] cnt[1*N]
#   note: N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); queries are O(log N), and only updates that add or drop a distinct value pay O(sqrt N) (one block rebuilt)
from bisect import bisect_left, bisect_right
from functools import reduce
from itertools import accumulate
from operator import and_, sub, xor


# Ordered multiset (online: any values, nothing known ahead), sqrt-style with a Fenwick tree inside every block: the
# distinct values in sorted blocks of LOAD..2*LOAD, each block keeping its values' copies and copies * value and xor plus a Fenwick
# tree over them, and a Fenwick tree over the block totals. Every query is two Fenwick walks (over blocks, then inside
# one), so O(log N); an update that adds or drops a distinct value rebuilds its block's Fenwick (O(sqrt N), C-level).


class BlockFenwickMultiset:
    LOAD = 64
    __slots__ = ("keys", "cnts", "fcs", "sums", "fss", "xvs", "fxs", "maxes", "bc", "fc", "bs", "fs", "bx", "fx", "cnt", "n", "lowV", "lowB", "lowC", "lowS", "highV", "highB", "highC", "mexV", "xtotal", "total", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.keys = []  # blocks of sorted distinct values
        self.cnts, self.fcs = [], []  # per block: copies of each value; Fenwick over them
        self.sums, self.fss = [], []  # per block: copies * value; Fenwick over them
        self.maxes = []  # last value of each block
        self.bc, self.fc = [], [0]  # per block: total copies; Fenwick over them
        self.bs, self.fs = [], [0]  # per block: total sum; Fenwick over them
        self.xvs, self.fxs = [], []  # per block: each value where its count is odd (else 0); xor Fenwick over them
        self.bx, self.fx = [], [0]  # per block: xor of those; xor Fenwick over them
        self.cnt = {}  # value -> copies
        self.xtotal = 0  # xor of all values (copies count)
        self.mexV = 0  # the mex, kept current (0 for the empty set)
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
        self.fx = self._buildx(self.bx)

    def _reinner(self, k):
        self.fcs[k] = self._build(self.cnts[k])
        self.fss[k] = self._build(self.sums[k])
        self.fxs[k] = self._buildx(self.xvs[k])

    def _insert(self, x, c):
        old = self.cnt.get(x, 0)
        if old:
            k = bisect_left(self.maxes, x)
            j = bisect_left(self.keys[k], x)
            self.bc[k] += c
            self._fen(self.fc, k, c)
            self.bs[k] += c * x
            self._fen(self.fs, k, c * x)
            if c & 1:  # x's parity flips
                self.bx[k] ^= x
                self._fenx(self.fx, k, x)
            if old + c:  # x stays: point updates only
                self.cnt[x] = old + c
                self.cnts[k][j] += c
                self._fen(self.fcs[k], j, c)
                self.sums[k][j] += c * x
                self._fen(self.fss[k], j, c * x)
                if c & 1:
                    self.xvs[k][j] ^= x
                    self._fenx(self.fxs[k], j, x)
                return old + c
            del self.cnt[x]
            self.d -= 1
            del self.keys[k][j], self.cnts[k][j]
            del self.sums[k][j]
            del self.xvs[k][j]
            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.fcs[k], self.maxes[k], self.bc[k]
                del self.sums[k], self.fss[k], self.bs[k]
                del self.xvs[k], self.fxs[k], self.bx[k]
                self._reblock()
                return 0
            self.maxes[k] = self.keys[k][-1]
            self._reinner(k)
            return 0
        self.cnt[x] = c
        self.d += 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
            self.fcs.append(None)
            self.sums.append([c * x])
            self.fss.append(None)
            self.bs.append(c * x)
            self.xvs.append([x if c & 1 else 0])
            self.fxs.append(None)
            self.bx.append(x if c & 1 else 0)
            self.maxes.append(x)
            self.bc.append(c)
            self._reinner(0)
            self._reblock()
            return c
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            k -= 1
        j = bisect_left(self.keys[k], x)
        self.keys[k].insert(j, x)
        self.cnts[k].insert(j, c)
        self.sums[k].insert(j, c * x)
        self.bs[k] += c * x
        self._fen(self.fs, k, c * x)
        self.xvs[k].insert(j, x if c & 1 else 0)
        if c & 1:
            self.bx[k] ^= x
            self._fenx(self.fx, k, x)
        self.maxes[k] = self.keys[k][-1]
        self.bc[k] += c
        self._fen(self.fc, k, c)
        if len(self.keys[k]) > 2 * self.LOAD:  # split the block in half
            h = self.LOAD
            for arr in (self.keys, self.cnts, self.sums, self.xvs):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.fcs.insert(k + 1, None)
            self.fss.insert(k + 1, None)
            self.fxs.insert(k + 1, None)
            self._reinner(k)
            self._reinner(k + 1)
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
            self.bs[k:k + 1] = [sum(self.sums[k]), sum(self.sums[k + 1])]
            self.bx[k:k + 1] = [reduce(xor, self.xvs[k], 0), reduce(xor, self.xvs[k + 1], 0)]
            self._reblock()
        else:
            self._reinner(k)
        return c

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

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps both medians, the mex current
        self.n += c
        self.total += c * x
        if c & 1:  # an odd number of copies flips x in or out of the xor of everything
            self.xtotal ^= x
        f = self._insert(x, c)  # x's new count
        n = self.n
        if c > 0:
            if x == self.mexV:  # x filled the mex
                self.mexV = self._findMex()
            if n == c:  # the set was empty
                self.lowV = self.highV = x
                self.lowB = self.highB = self.lowS = 0
                self.lowC = self.highC = c
                return
        else:
            if 0 <= x < self.mexV and not f:  # the last copy of a value below the mex
                self.mexV = x
            if not n:
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

    def _sumFirst(self, k):  # sum of the k smallest values
        if k <= 0:
            return 0
        v, b, _, s = self._kthInfo(k)
        return s + (k - b) * v

    def _resetCached(self):  # nothing counted: as newly built
        self.mexV = 0
        self.n = self.d = 0
        self.total = 0
        self.xtotal = 0

    def _clearData(self):
        self.keys, self.cnts, self.fcs, self.maxes, self.bc = [], [], [], [], []
        self.fc = [0]
        self.cnt = {}
        self.sums, self.fss, self.bs = [], [], []
        self.fs = [0]
        self.xvs, self.fxs, self.bx = [], [], []
        self.fx = [0]

    def _distinctLt(self, x):  # distinct values < x: every block before x's, then a binary search in x's block
        keys = self.keys
        b = bisect_left(self.maxes, x)
        return sum(map(len, keys[:b])) + (bisect_left(keys[b], x) if b < len(keys) else 0)

    @staticmethod
    def _buildx(a):  # xor Fenwick over a, in C-level passes like _build
        p = list(accumulate(a, xor, initial=0))
        m = len(p)
        return list(map(xor, p, map(p.__getitem__, map(and_, range(m), range(-1, m - 1)))))

    @staticmethod
    def _fenx(f, i, v):
        i += 1
        while i < len(f):
            f[i] ^= v
            i += i & -i

    @staticmethod
    def _xpre(f, i):  # xor over positions 0..i-1
        res = 0
        while i > 0:
            res ^= f[i]
            i &= i - 1
        return res

    def _xlt(self, x):  # xor of the values < x (copies count)
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.xtotal
        return self._xpre(self.fx, k) ^ self._xpre(self.fxs[k], bisect_left(self.keys[k], x))

    def _xle(self, x):  # xor of the values <= x (copies count)
        k = bisect_right(self.maxes, x)
        if k == len(self.keys):
            return self.xtotal
        return self._xpre(self.fx, k) ^ self._xpre(self.fxs[k], bisect_right(self.keys[k], x))

    def _xorFirst(self, k):  # xor of the k smallest values (copies count): lift over blocks, then inside one
        if k <= 0:
            return 0
        fc, fx = self.fc, self.fx
        m = len(self.bc)
        b, before, res = 0, 0, 0
        step = 1 << (m.bit_length() - 1)
        while step:
            nxt = b + step
            if nxt <= m and before + fc[nxt] < k:
                b = nxt
                before += fc[nxt]
                res ^= fx[nxt]
            step >>= 1
        f, g = self.fcs[b], self.fxs[b]
        m = len(self.keys[b])
        j = 0
        step = 1 << (m.bit_length() - 1)
        while step:
            nxt = j + step
            if nxt <= m and before + f[nxt] < k:
                j = nxt
                before += f[nxt]
                res ^= g[nxt]
            step >>= 1
        return res ^ self.keys[b][j] if (k - before) & 1 else res  # k - before copies of the answer's value

    # O(sqrtN) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(sqrtN) -- add cnt copies of val (nothing if cnt <= 0)
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

    # O(sqrtN) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
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

    # O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        return self.highV if self.n else None

    # O(1) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        return self.lowV if self.n else None

    # O(1) -- smallest non-negative integer not in the set
    def mex(self):
        return self.mexV

    # O(logN) -- smallest value; None if empty
    def min(self):
        return self._kth(1) if self.n else None

    # O(sqrtN) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(sqrtN) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(sqrtN) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self._kth(1)
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

    # O(sqrtN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    # O(1) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    def sumAbsDiffToMedian(self):
        if not self.n:
            return 0
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

    # O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    def xorOfAll(self):
        return self.xtotal

    # O(logN) -- xor of the values > x (copies count)
    def xorOfGtX(self, x):
        return self.xtotal ^ self._xle(x)

    # O(logN) -- xor of the values >= x (copies count)
    def xorOfGteX(self, x):
        return self.xtotal ^ self._xlt(x)

    # O(logN) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    def xorOfInValRange(self, lo, hi):
        return self._xle(hi) ^ self._xlt(lo) if lo <= hi else 0

    # O(logN) -- xor of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def xorOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._xorFirst(self.n - kFrom + 1) ^ self._xorFirst(self.n - kTo)

    # O(logN) -- xor of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def xorOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._xorFirst(kTo) ^ self._xorFirst(kFrom - 1)

    # O(logN) -- xor of the k largest values (copies count); raises IndexError unless 0 <= k <= size
    def xorOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.xtotal ^ self._xorFirst(self.n - k)

    # O(logN) -- xor of the values < x (copies count)
    def xorOfLtX(self, x):
        return self._xlt(x)

    # O(logN) -- xor of the values <= x (copies count)
    def xorOfLteX(self, x):
        return self._xle(x)

    # O(logN) -- xor of the k smallest values (copies count); raises IndexError unless 0 <= k <= size
    def xorOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._xorFirst(k)
