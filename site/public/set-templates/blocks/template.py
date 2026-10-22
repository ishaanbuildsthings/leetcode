# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/blocks/template.py
# @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow mex min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX
# @data-structure-type: blocks
# @values: online
# @complexities:
#   add: sqrt(N)
#   addCount: sqrt(N)
#   count: log(N)
#   countDistinct: 1
#   countGtX: sqrt(N)
#   countGteX: sqrt(N)
#   countInValRange: sqrt(N)
#   countLtX: sqrt(N)
#   countLteX: sqrt(N)
#   kthLargest: sqrt(N)
#   kthSmallest: sqrt(N)
#   largestLtX: sqrt(N)
#   largestLteX: sqrt(N)
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
#   smallestGtX: sqrt(N)
#   smallestGteX: sqrt(N)
#   build: 1
# @memory:
#   layout: none
#   node: keys[1*N] cnts[1*N]
#   tags: none
#   other: maxes[1*sqrt(N)] bc[2*sqrt(N)] cnt[1*N]
#   note: N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); each operation costs a few binary searches plus one block's worth of C-level list work
from bisect import bisect_left, bisect_right, insort
from itertools import accumulate


# Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
# LOAD..2*LOAD, each block keeping its values' copies plus block totals, and a Fenwick tree over the
# block totals (rebuilt only after a block splits or empties). A query finds its block by binary search (or by
# lifting over the block Fenwick for k-th) and then works inside one block with C-level list operations.


class BlockMultiset:
    LOAD = 64
    __slots__ = ("keys", "cnts", "maxes", "bc", "fc", "cnt", "n", "mn", "mx", "med", "lowV", "lowB", "lowC", "highV", "highB", "highC", "mexV", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.keys = []  # blocks of sorted distinct values
        self.cnts = []  # per block: copies of each value
        self.maxes = []  # last value of each block
        self.bc = []  # per block: total copies
        self.fc = None  # Fenwick over bc (None: stale)
        self.cnt = {}  # value -> copies
        self.med, self.mexV = False, -1  # medians / mex are tracked from their first query on; min / max always (set by the first add)
        self.n = self.d = 0

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
        f = self.fc if which == 0 else None
        if f is None:
            f = self._build(self.bc if which == 0 else None)
            if which == 0:
                self.fc = f
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
                self.bc[k] += c
                self._fen(self.fc, k, c)
                return
            del self.cnt[x]
            self.d -= 1
            del self.keys[k][j], self.cnts[k][j]
            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.maxes[k], self.bc[k]
                self.fc = None
                return
            self.maxes[k] = self.keys[k][-1]
            self.bc[k] += c
            self._fen(self.fc, k, c)
            return
        self.cnt[x] = c
        self.d += 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
            self.maxes.append(x)
            self.bc.append(c)
            self.fc = None
            return
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            k -= 1
        j = bisect_left(self.keys[k], x)
        self.keys[k].insert(j, x)
        self.cnts[k].insert(j, c)
        self.maxes[k] = self.keys[k][-1]
        self.bc[k] += c
        self._fen(self.fc, k, c)
        if len(self.keys[k]) > 2 * self.LOAD:  # split the block in half
            h = self.LOAD
            for arr in (self.keys, self.cnts):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
            self.fc = None

    def _count(self, x, strict, which):  # copies (which=0) of the values < x (strict) or <= x
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.n
        j = (bisect_left if strict else bisect_right)(self.keys[k], x)
        return self._pre(which, k) + sum((self.cnts)[k][:j])

    def _lt(self, x):
        return self._count(x, True, 0)

    def _le(self, x):
        return self._count(x, False, 0)

    def _countOf(self, x):
        return self.cnt.get(x, 0)

    def _locate(self, k):  # (block, copies before it, 0) for the block holding the k-th smallest
        self._pre(0, 0)
        fc = self.fc
        pos, before, acc = 0, 0, 0
        step = 1 << (len(self.bc).bit_length() - 1) if self.bc else 0
        while step:
            nxt = pos + step
            if nxt <= len(self.bc) and before + fc[nxt] < k:
                pos = nxt
                before += fc[nxt]
            step >>= 1
        return pos, before, acc

    def _kth(self, k):
        b, before, _ = self._locate(k)
        return self.keys[b][bisect_left(list(accumulate(self.cnts[b])), k - before)]
    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies)
        b, before, acc = self._locate(k)
        cn = self.cnts[b]
        pre = list(accumulate(cn))
        j = bisect_left(pre, k - before)
        return self.keys[b][j], before + pre[j] - cn[j], cn[j]
    # smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, 2, ...
    def _findMex(self):
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
        self._insert(x, c)
        n = self.n
        if c > 0:
            if x == self.mexV and x >= 0:  # x filled the mex (mexV is -1 until mex() is first called)
                self.mexV = self._findMex()
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

    # O(sqrtN) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(sqrtN) -- add c copies of x (nothing if c <= 0)
    def addCount(self, x, c):
        if c > 0:
            self._add(x, c)

    # O(logN) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(sqrtN) -- how many values > x
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(sqrtN) -- how many values >= x
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(sqrtN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(sqrtN) -- how many values < x
    def countLtX(self, x):
        return self._lt(x)

    # O(sqrtN) -- how many values <= x
    def countLteX(self, x):
        return self._le(x)

    # O(sqrtN) -- k-th largest value (1-indexed); raises IndexError unless 1 <= k <= size
    def kthLargest(self, k):
        if not 1 <= k <= self.n:
            raise IndexError(f"kthLargest: needs 1 <= k <= size, got k = {k}, size = {self.n}")
        return self._kth(self.n - k + 1)

    # O(sqrtN) -- k-th smallest value (1-indexed); raises IndexError unless 1 <= k <= size
    def kthSmallest(self, k):
        if not 1 <= k <= self.n:
            raise IndexError(f"kthSmallest: needs 1 <= k <= size, got k = {k}, size = {self.n}")
        return self._kth(k)

    # O(sqrtN) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(sqrtN) -- largest value <= x; None if there is none
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

    # O(sqrtN) -- remove every copy of x; returns how many were removed
    def removeAll(self, x):
        k = self.count(x)
        if k:
            self._add(x, -k)
        return k

    # O(sqrtN) -- remove min(c, count(x)) copies of x; returns how many were removed
    def removeCount(self, x, c):
        k = min(c, self.count(x))
        if k <= 0:
            return 0
        self._add(x, -k)
        return k

    # O(1) -- how many values (copies count)
    def size(self):
        return self.n

    # O(sqrtN) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(sqrtN) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None
