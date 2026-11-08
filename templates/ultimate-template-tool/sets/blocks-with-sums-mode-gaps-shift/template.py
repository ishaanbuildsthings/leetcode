# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/blocks-with-sums-mode-gaps-shift/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff mode pop popMax popMin remove removeAll removeCount removeInValRange shiftAll size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: blocks
# @values: online
# @keys: numbers
# @tracks: mode gaps shift
# @complexities:
#   add: sqrt(N) amortized
#   addCount: sqrt(N) amortized
#   clear: 1 amortized
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
#   max: sqrt(N)
#   maxGap: 1 amortized
#   medianHigh: sqrt(N)
#   medianLow: sqrt(N)
#   mex: sqrt(N)
#   min: sqrt(N)
#   minAdjacentDiff: 1 amortized
#   mode: 1
#   pop: sqrt(N) amortized
#   popMax: sqrt(N) amortized
#   popMin: sqrt(N) amortized
#   remove: sqrt(N) amortized
#   removeAll: sqrt(N) amortized
#   removeCount: sqrt(N) amortized
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
#   other: maxes[29*sqrt(N)] bc[58*sqrt(N)] bs[58*sqrt(N)] cnt[1*N]
#   note: N = distinct values present; blocks of max(LOAD, sqrt(N) / 8) values (LOAD: Python 64, C++ 512), all cut again once N / 2 distinct values have come or gone; each operation costs a few binary searches plus one block's worth of C-level list work
from random import getrandbits
from heapq import heappop, heappush
from bisect import bisect_left, bisect_right, insort
from itertools import accumulate, chain
from math import isqrt


# Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
# max(LOAD, sqrt(N) / 8), each block keeping its values' copies and copies * value plus block totals, and a Fenwick tree over the
# block totals (rebuilt only after a block splits or empties). A block splits in half past twice the block size, and
# once N / 2 distinct values have come or gone since the last cut, every block is cut again at that size: blocks
# follow sqrt(N) as N grows or shrinks (small blocks are faster in practice; any constant times sqrt(N) keeps the
# bounds), and the O(N) cut is paid for by those N / 2 updates. A query
# finds its block by binary search (or by lifting over the block Fenwick for k-th) and then works inside one block
# with C-level list operations.


class BlockMultiset:
    LOAD = 64  # the smallest block size (sqrt(N) / 8 once N passes (8 * LOAD)^2)
    __slots__ = ("load", "due", "keys", "cnts", "sums", "maxes", "bc", "bs", "fc", "fs", "cnt", "n", "bk", "bkAt", "fh", "fhAt", "gc", "gmin", "gmax", "dups", "off", "salt", "total", "d")

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
        self.load, self.due = self.LOAD, self.LOAD * self.LOAD >> 1  # block size; distinct values to add / drop before a cut
        self.salt = getrandbits(60)  # hash containers key on salted values, so no fixed input can force collisions
        self.off = 0  # every value v is stored as v - off: shiftAll only moves off
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.bk, self.bkAt = {}, {}  # mode: count -> list of the values with that many copies; value -> its index there
        self.fh, self.fhAt = [], {}  # mode: max-heap of the counts that have a bucket; count -> its index in it
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
        if self.due <= 0:  # enough distinct values came or went: cut the blocks again
            self._recut()
        old = self.cnt.get(x ^ self.salt if x.__class__ is int else x, 0)
        if old:
            k = bisect_left(self.maxes, x)
            j = bisect_left(self.keys[k], x)
            if old + c:
                self.cnt[x ^ self.salt if x.__class__ is int else x] = old + c
                self.cnts[k][j] += c
                self.sums[k][j] += c * x
                self.bc[k] += c
                self._fen(self.fc, k, c)
                self.bs[k] += c * x
                self._fen(self.fs, k, c * x)
                return old + c
            del self.cnt[x ^ self.salt if x.__class__ is int else x]
            self.d -= 1
            self.due -= 1
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
        self.cnt[x ^ self.salt if x.__class__ is int else x] = c
        self.d += 1
        self.due -= 1
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
        if len(self.keys[k]) > 2 * self.load:  # split the block in half
            h = self.load
            for arr in (self.keys, self.cnts, self.sums):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
            self.bs[k:k + 1] = [sum(self.sums[k]), sum(self.sums[k + 1])]
            self.fc = self.fs = None
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
        sums = list(chain.from_iterable(self.sums))
        self.keys = [keys[i:i + h] for i in range(0, d, h)]
        self.cnts = [cnts[i:i + h] for i in range(0, d, h)]
        self.sums = [sums[i:i + h] for i in range(0, d, h)]
        self.maxes = [b[-1] for b in self.keys]
        self.bc = list(map(sum, self.cnts))
        self.bs = list(map(sum, self.sums))
        self.fc = self.fs = None

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
        return self.cnt.get(x ^ self.salt if x.__class__ is int else x, 0)

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

    def _add(self, x, c):  # c copies of x (c < 0 removes)
        self.n += c
        self.total += c * x
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

    def _sumFirst(self, k):  # sum of the k smallest values
        if k <= 0:
            return 0
        v, b, _, s = self._kthInfo(k)
        return s + (k - b) * v

    def _resetCached(self):  # nothing counted: as newly built
        self.bk, self.bkAt, self.fh, self.fhAt = {}, {}, [], {}
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0
        self.n = self.d = 0
        self.total = 0
        self.off = 0

    def _clearData(self):
        self.keys, self.cnts, self.maxes, self.bc = [], [], [], []
        self.fc = None
        self.load, self.due = self.LOAD, self.LOAD * self.LOAD >> 1
        self.cnt = {}
        self.sums, self.bs = [], []
        self.fs = None

    def _distinctLt(self, x):  # distinct values < x: every block before x's, then a binary search in x's block
        keys = self.keys
        b = bisect_left(self.maxes, x)
        return sum(map(len, keys[:b])) + (bisect_left(keys[b], x) if b < len(keys) else 0)

    # O(sqrtN amortized) -- add one copy of x
    def add(self, x):
        x -= self.off
        self._add(x, 1)

    # O(sqrtN amortized) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        val -= self.off
        if cnt > 0:
            self._add(val, cnt)

    # O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    # instead of building a new one
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

    # O(sqrtN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in
    # the set
    def firstIndex(self, x):
        x -= self.off
        return self._lt(x) if self._countOf(x) else -1

    # O(sqrtN) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    # kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); raises IndexError unless 0 <= i < size
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

    # O(sqrtN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is
    # not in the set
    def lastIndex(self, x):
        x -= self.off
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(sqrtN) -- largest value; raises IndexError if empty
    def max(self):
        if not self.n:
            raise IndexError("max: the set is empty")
        return self._kth(self.n) + self.off

    # O(1 amortized) -- largest difference between two neighbouring distinct values; None if fewer than 2 distinct
    # values
    def maxGap(self):
        return self._maxGap() if self.d >= 2 else None

    # O(sqrtN) -- upper median: the (floor(size/2) + 1)-th smallest value; raises IndexError if empty
    def medianHigh(self):
        if not self.n:
            raise IndexError("medianHigh: the set is empty")
        return self._kth((self.n >> 1) + 1) + self.off

    # O(sqrtN) -- lower median: the ceil(size/2)-th smallest value; raises IndexError if empty
    def medianLow(self):
        if not self.n:
            raise IndexError("medianLow: the set is empty")
        return self._kth((self.n + 1) >> 1) + self.off

    # O(sqrtN) -- smallest non-negative integer not in the set
    def mex(self):
        return self._findMex() + self.off

    # O(sqrtN) -- smallest value; raises IndexError if empty
    def min(self):
        if not self.n:
            raise IndexError("min: the set is empty")
        return self._kth(1) + self.off

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
        return (v ^ self.salt if v.__class__ is int else v) + self.off, f

    # O(sqrtN amortized) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (=
    # popMin()), pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v + self.off

    # O(sqrtN amortized) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self._kth(self.n)
        self._add(v, -1)
        return v + self.off

    # O(sqrtN amortized) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self._kth(1)
        self._add(v, -1)
        return v + self.off

    # O(sqrtN amortized) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        x -= self.off
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(sqrtN amortized) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        val -= self.off
        k = self._countOf(val)
        if k:
            self._add(val, -k)
        return k

    # O(sqrtN amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed
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

    # O(sqrtN) -- sum of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    # largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises IndexError unless
    # 1 <= kFrom <= kTo <= size
    def sumKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._sumFirst(self.n - kFrom + 1) - self._sumFirst(self.n - kTo) + self.off * (kTo - kFrom + 1)

    # O(sqrtN) -- sum of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    # smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError unless 1
    # <= kFrom <= kTo <= size
    def sumKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._sumFirst(kTo) - self._sumFirst(kFrom - 1) + self.off * (kTo - kFrom + 1)

    # O(sqrtN) -- sum of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    # the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); raises IndexError unless 0 <=
    # k <= size
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

    # O(sqrtN) -- sum of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1
    # just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); raises IndexError
    # unless 0 <= k <= size
    def sumSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._sumFirst(k) + self.off * k
