# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/blocks-fenwick-with-cachedmex-minmax-medians-mode-gaps/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff mode pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
# @data-structure-type: blocks-fenwick
# @values: online
# @keys: numbers
# @tracks: minmax medians mex mode gaps
# @complexities:
#   add: sqrt(N) amortized
#   addCount: sqrt(N) amortized
#   clear: 1 amortized
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
#   max: 1
#   maxGap: 1 amortized
#   medianHigh: 1
#   medianLow: 1
#   mex: 1
#   min: 1
#   minAdjacentDiff: 1 amortized
#   mode: 1
#   pop: sqrt(N) amortized
#   popMax: sqrt(N) amortized
#   popMin: sqrt(N) amortized
#   remove: sqrt(N) amortized
#   removeAll: sqrt(N) amortized
#   removeCount: sqrt(N) amortized
#   removeInValRange: sqrt(N) amortized
#   size: 1
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   build: 1
# @memory:
#   layout: none
#   node: keys[1*N] cnts[1*N] fcs[1*N]
#   tags: none
#   other: maxes[29*sqrt(N)] bc[58*sqrt(N)] cnt[1*N]
#   note: N = distinct values present; blocks of max(LOAD, sqrt(N) / 8) values (LOAD: Python 64, C++ 512), all cut again once N / 2 distinct values have come or gone; queries are O(log N), and only updates that add or drop a distinct value pay O(sqrt N) (one block rebuilt; amortized: a cut now and then)
from random import getrandbits
from heapq import heappop, heappush
from bisect import bisect_left, bisect_right
from itertools import accumulate, chain
from math import isqrt
from operator import and_, sub


# Ordered multiset (online: any values, nothing known ahead), sqrt-style with a Fenwick tree inside every block: the
# distinct values in sorted blocks of max(LOAD, sqrt(N) / 8), each block keeping its values' copies plus a Fenwick
# tree over them, and a Fenwick tree over the block totals. Every query is two Fenwick walks (over blocks, then inside
# one), so O(log N); an update that adds or drops a distinct value rebuilds its block's Fenwick (O(sqrt N), C-level).
# A block splits in half past twice the block size, and once N / 2 distinct values have come or gone since the last
# cut, every block is cut again at that size: the O(N) cut is paid for by those N / 2 updates.


class BlockFenwickMultiset:
    LOAD = 64  # the smallest block size (sqrt(N) / 8 once N passes (8 * LOAD)^2)
    __slots__ = ("load", "due", "keys", "cnts", "fcs", "maxes", "bc", "fc", "cnt", "n", "mn", "mx", "lowV", "lowB", "lowC", "highV", "highB", "highC", "mexV", "bk", "bkAt", "fh", "fhAt", "gc", "gmin", "gmax", "dups", "salt", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.keys = []  # blocks of sorted distinct values
        self.cnts, self.fcs = [], []  # per block: copies of each value; Fenwick over them
        self.maxes = []  # last value of each block
        self.bc, self.fc = [], [0]  # per block: total copies; Fenwick over them
        self.cnt = {}  # value -> copies
        self.load, self.due = self.LOAD, self.LOAD * self.LOAD >> 1  # block size; distinct values to add / drop before a cut
        self.salt = getrandbits(60)  # hash containers key on salted values, so no fixed input can force collisions
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.bk, self.bkAt = {}, {}  # mode: count -> list of the values with that many copies; value -> its index there
        self.fh, self.fhAt = [], {}  # mode: max-heap of the counts that have a bucket; count -> its index in it
        self.mexV = 0  # the mex, kept current (0 for the empty set)
        self.n = self.d = 0

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

    def _reinner(self, k):
        self.fcs[k] = self._build(self.cnts[k])

    def _insert(self, x, c):
        if self.due <= 0:  # enough distinct values came or went: cut the blocks again
            self._recut()
        old = self.cnt.get(x ^ self.salt if x.__class__ is int else x, 0)
        if old:
            k = bisect_left(self.maxes, x)
            j = bisect_left(self.keys[k], x)
            self.bc[k] += c
            self._fen(self.fc, k, c)
            if old + c:  # x stays: point updates only
                self.cnt[x ^ self.salt if x.__class__ is int else x] = old + c
                self.cnts[k][j] += c
                self._fen(self.fcs[k], j, c)
                return old + c
            del self.cnt[x ^ self.salt if x.__class__ is int else x]
            self.d -= 1
            self.due -= 1
            del self.keys[k][j], self.cnts[k][j]
            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.fcs[k], self.maxes[k], self.bc[k]
                self._reblock()
                return 0
            self.maxes[k] = self.keys[k][-1]
            self._reinner(k)
            return 0
        self.cnt[x ^ self.salt if x.__class__ is int else x] = c
        self.d += 1
        self.due -= 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
            self.fcs.append(None)
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
        self.maxes[k] = self.keys[k][-1]
        self.bc[k] += c
        self._fen(self.fc, k, c)
        if len(self.keys[k]) > 2 * self.load:  # split the block in half
            h = self.load
            for arr in (self.keys, self.cnts):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.fcs.insert(k + 1, None)
            self._reinner(k)
            self._reinner(k + 1)
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
            self._reblock()
        else:
            self._reinner(k)
        return c

    def _recut(self):  # every block cut again at sqrt(N) / 8: O(N), once per N / 2 updates that add or drop a value
        d = self.d
        h = max(self.LOAD, isqrt(d) >> 3)
        self.due = max(d, self.LOAD * self.LOAD) >> 1
        if h == self.load and len(self.keys) <= d // h + 1:  # same size, blocks still full on average
            return
        self.load = h
        keys = list(chain.from_iterable(self.keys))
        cnts = list(chain.from_iterable(self.cnts))
        self.keys = [keys[i:i + h] for i in range(0, d, h)]
        self.cnts = [cnts[i:i + h] for i in range(0, d, h)]
        self.fcs = list(map(self._build, self.cnts))
        self.maxes = [b[-1] for b in self.keys]
        self.bc = list(map(sum, self.cnts))
        self._reblock()

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

    def _countOf(self, x):
        return self.cnt.get(x ^ self.salt if x.__class__ is int else x, 0)

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies): lift over blocks, then inside one
        fc = self.fc
        m = len(self.bc)
        b, before = 0, 0
        step = 1 << (m.bit_length() - 1)
        while step:
            nxt = b + step
            if nxt <= m and before + fc[nxt] < k:
                b = nxt
                before += fc[nxt]
            step >>= 1
        f = self.fcs[b]
        m = len(self.keys[b])
        j = 0
        step = 1 << (m.bit_length() - 1)
        while step:
            nxt = j + step
            if nxt <= m and before + f[nxt] < k:
                j = nxt
                before += f[nxt]
            step >>= 1
        return self.keys[b][j], before, self.cnts[b][j]

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

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max, both medians, the mex current
        self.n += c
        f = self._insert(x, c)  # x's new count
        g = f - c  # x's old count
        # mode: x moves from the bucket of its old count to its new one (a bucket is a list, and x's index in it is
        # kept, so x leaves by swapping in the bucket's last value); a bucket that appears or empties adds or drops
        # its count in the max-heap of counts: O(log N) worst case, however far a count jumps
        salt, bk, at = self.salt, self.bk, self.bkAt
        key = x ^ salt if x.__class__ is int else x  # (salted: no fixed input can force dict collisions)
        gone = 0  # a count whose bucket emptied (its heap slot goes to x's new count if that one is new)
        if g:
            vs = bk[g ^ salt]
            last = vs.pop()
            if vs:
                i = at[key]
                if i < len(vs):
                    vs[i] = last
                    at[last] = i
            else:
                del bk[g ^ salt]
                gone = g
        if f:
            vs = bk.get(f ^ salt)
            if vs is None:
                bk[f ^ salt] = [key]
                at[key] = 0
                self._swapFreq(gone, f)
                gone = 0
            else:
                at[key] = len(vs)
                vs.append(key)
        else:
            del at[key]
        if gone:
            self._swapFreq(gone, 0)
        if (g >= 2) != (f >= 2):  # values with 2+ copies (then the smallest difference is 0)
            self.dups += 1 if f >= 2 else -1
        if not g or not f:  # x appeared or disappeared: the gap between its neighbours splits or comes back
            i = self._lt(x)  # (one walk: the copies of x are known, and stored values skip any shift)
            j = i + f
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
            if x == self.mexV:  # x filled the mex
                self.mexV = self._findMex()
            if n == c:  # the set was empty
                self.mn = self.mx = x
                self.lowV = self.highV = x
                self.lowB = self.highB = 0
                self.lowC = self.highC = c
                return
            if x < self.mn:
                self.mn = x
            if x > self.mx:
                self.mx = x
        else:
            if 0 <= x < self.mexV and not f:  # the last copy of a value below the mex
                self.mexV = x
            if not n:
                return
            if not f:  # x is gone: it may have been the min / max
                if x == self.mn:
                    self.mn = self._kth(1)
                if x == self.mx:
                    self.mx = self._kth(n)
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

    def _swapFreq(self, old, new):  # in the max-heap of counts, count old (0: none) becomes count new (0: none), O(log N)
        h, at, salt = self.fh, self.fhAt, self.salt  # (fhAt: count -> its index in the heap)
        if old:
            i = at.pop(old ^ salt)
            if not new:  # old leaves: the heap's last count fills its slot
                new = h.pop()
                if i == len(h):
                    return
        else:
            i = len(h)
            h.append(new)
        m = len(h)
        while i:  # up while bigger than its parent
            p = (i - 1) >> 1
            if h[p] >= new:
                break
            h[i] = h[p]
            at[h[p] ^ salt] = i
            i = p
        while True:  # down while a child is bigger
            c = 2 * i + 1
            if c >= m:
                break
            if c + 1 < m and h[c + 1] > h[c]:
                c += 1
            if h[c] <= new:
                break
            h[i] = h[c]
            at[h[c] ^ salt] = i
            i = c
        h[i] = new
        at[new ^ salt] = i

    def _gap(self, g, c):  # one more (c = 1) / fewer (c = -1) gap of size g
        gc, key = self.gc, g ^ self.salt
        k = gc.get(key, 0) + c
        if k:
            gc[key] = k
            if k == 1 and c > 0:  # (a size already present has an entry in both heaps)
                if len(self.gmin) > 2 * len(gc) + 8:  # mostly sizes no longer present: rebuild from the live ones
                    self.gmin = sorted(v ^ self.salt for v in gc)
                    self.gmax = [-v for v in reversed(self.gmin)]
                else:
                    heappush(self.gmin, g)
                    heappush(self.gmax, -g)
        else:
            del gc[key]

    def _minGap(self):  # heap tops of sizes no longer present are dropped as they surface
        h, gc, salt = self.gmin, self.gc, self.salt
        while h[0] ^ salt not in gc:
            heappop(h)
        return h[0]

    def _maxGap(self):
        h, gc, salt = self.gmax, self.gc, self.salt
        while -h[0] ^ salt not in gc:
            heappop(h)
        return -h[0]

    def _resetCached(self):  # nothing counted: as newly built
        self.mexV = 0
        self.bk, self.bkAt, self.fh, self.fhAt = {}, {}, [], {}
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0
        self.n = self.d = 0

    def _clearData(self):
        self.keys, self.cnts, self.fcs, self.maxes, self.bc = [], [], [], [], []
        self.load, self.due = self.LOAD, self.LOAD * self.LOAD >> 1
        self.fc = [0]
        self.cnt = {}

    def _distinctLt(self, x):  # distinct values < x: every block before x's, then a binary search in x's block
        keys = self.keys
        b = bisect_left(self.maxes, x)
        return sum(map(len, keys[:b])) + (bisect_left(keys[b], x) if b < len(keys) else 0)

    # O(sqrtN amortized) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(sqrtN amortized) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    # instead of building a new one
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

    # O(logN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in
    # the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(logN) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    # kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); raises IndexError unless 0 <= i < size
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

    # O(logN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is
    # not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(1) -- largest value; raises IndexError if empty
    def max(self):
        if not self.n:
            raise IndexError("max: the set is empty")
        return self.mx

    # O(1 amortized) -- largest difference between two neighbouring distinct values; None if fewer than 2 distinct
    # values
    def maxGap(self):
        return self._maxGap() if self.d >= 2 else None

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

    # O(1) -- smallest value; raises IndexError if empty
    def min(self):
        if not self.n:
            raise IndexError("min: the set is empty")
        return self.mn

    # O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); None if fewer
    # than 2 values
    def minAdjacentDiff(self):
        if self.n < 2:
            return None
        return 0 if self.dups else self._minGap()

    # O(1) -- (a most frequent value, its count); raises IndexError if empty. C++ returns the smallest of the most
    # frequent values
    def mode(self):
        if not self.n:
            raise IndexError("mode: the set is empty")
        f = self.fh[0]
        v = self.bk[f ^ self.salt][0]
        return (v ^ self.salt if v.__class__ is int else v), f

    # O(sqrtN amortized) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (=
    # popMin()), pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(sqrtN amortized) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self.mx
        self._add(v, -1)
        return v

    # O(sqrtN amortized) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self.mn
        self._add(v, -1)
        return v

    # O(sqrtN amortized) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(sqrtN amortized) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(sqrtN amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed
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
