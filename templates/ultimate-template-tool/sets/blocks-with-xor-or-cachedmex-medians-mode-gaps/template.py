# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/blocks-with-xor-or-cachedmex-medians-mode-gaps/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff mode orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
# @data-structure-type: blocks
# @values: online
# @keys: numbers
# @tracks: medians mex mode gaps
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
#   medianHigh: 1
#   medianLow: 1
#   mex: 1
#   min: sqrt(N)
#   minAdjacentDiff: 1 amortized
#   mode: 1
#   orOfAll: sqrt(N)
#   orOfGtX: sqrt(N)
#   orOfGteX: sqrt(N)
#   orOfInValRange: sqrt(N)
#   orOfKthLargestRange: sqrt(N)
#   orOfKthSmallestRange: sqrt(N)
#   orOfLargestK: sqrt(N)
#   orOfLtX: sqrt(N)
#   orOfLteX: sqrt(N)
#   orOfSmallestK: sqrt(N)
#   pop: sqrt(N) amortized
#   popMax: sqrt(N) amortized
#   popMin: sqrt(N) amortized
#   remove: sqrt(N) amortized
#   removeAll: sqrt(N) amortized
#   removeCount: sqrt(N) amortized
#   removeInValRange: sqrt(N) amortized
#   size: 1
#   smallestGtX: sqrt(N)
#   smallestGteX: sqrt(N)
#   xorOfAll: 1
#   xorOfGtX: sqrt(N)
#   xorOfGteX: sqrt(N)
#   xorOfInValRange: sqrt(N)
#   xorOfKthLargestRange: sqrt(N)
#   xorOfKthSmallestRange: sqrt(N)
#   xorOfLargestK: sqrt(N)
#   xorOfLtX: sqrt(N)
#   xorOfLteX: sqrt(N)
#   xorOfSmallestK: sqrt(N)
#   build: 1
# @memory:
#   layout: none
#   node: keys[1*N] cnts[1*N]
#   tags: none
#   other: maxes[20*sqrt(N)+2] bc[40*sqrt(N)+5] bx[40*sqrt(N)+5] bo[20*sqrt(N)+2] cnt[1*N]
#   note: N = distinct values present; blocks of max(LOAD, sqrt(N) / 8) values (LOAD: Python 64, C++ 512), all cut again once N / 2 distinct values have come or gone, or once there are more than 2 * N / size + 2 blocks; each operation costs a few binary searches plus one block's worth of C-level list work
from random import getrandbits
from heapq import heappop, heappush
from bisect import bisect_left, bisect_right, insort
from functools import reduce
from itertools import accumulate, chain, compress, repeat
from math import isqrt
from operator import and_, or_, xor


# Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
# max(LOAD, sqrt(N) / 8), each block keeping its values' copies plus block totals and each block's xor / OR, and a
# Fenwick tree over the block totals (rebuilt only after a block splits or empties). A block splits in half past twice
# the block size, and once N / 2 distinct values have come or gone since the last cut, every block is cut again at that
# size: blocks follow sqrt(N) as N grows or shrinks (small blocks are faster in practice; any constant times sqrt(N)
# keeps the bounds). The blocks are also cut again as soon as there are more than 2 * N / size + 2 of them (removals can
# leave many small blocks), so there are never more than 20 sqrt(N) + 2. A cut is O(N), paid for by the N / 4 or more
# updates since the last one. A query finds its block by binary search (or by lifting over the block Fenwick for k-th)
# and then works inside one block with C-level list operations.


class BlockMultiset:
    LOAD = 64  # the smallest block size (sqrt(N) / 8 once N passes (8 * LOAD)^2)
    __slots__ = ("load", "due", "keys", "cnts", "maxes", "bc", "fc", "bx", "fx", "bo", "cnt", "n", "lowV", "lowB",
        "lowC", "highV", "highB", "highC", "mexV", "bk", "bkAt", "fh", "fhAt", "gc", "gmin", "gmax", "dups", "xtotal",
        "salt", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.keys = []  # blocks of sorted distinct values
        self.cnts = []  # per block: copies of each value
        self.maxes = []  # last value of each block
        self.bc = []  # per block: total copies
        self.fc = None  # Fenwick over bc (None: stale)
        self.bx = []  # per block: xor of the values with an odd count
        self.fx = None  # xor Fenwick over bx (None: stale)
        self.bo = []  # per block: OR of its values
        self.cnt = {}  # value -> copies
        # block size; distinct values to add / drop before a cut
        self.load, self.due = self.LOAD, self.LOAD * self.LOAD >> 1
        self.salt = getrandbits(60)  # hash containers key on salted values, so no fixed input can force collisions
        self.xtotal = 0  # xor of all values (copies count)
        # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0
        self.bk, self.bkAt = {}, {}  # mode: count -> list of the values with that many copies; value -> its index there
        self.fh, self.fhAt = [], {}  # mode: max-heap of the counts that have a bucket; count -> its index in it
        self.mexV = 0  # the mex, kept current (0 for the empty set)
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
        if self.due <= 0:  # enough distinct values came or went: cut the blocks again
            self._recut()
        old = self.cnt.get(x ^ self.salt if x.__class__ is int else x, 0)
        if old:
            k = bisect_left(self.maxes, x)
            j = bisect_left(self.keys[k], x)
            if c & 1:  # x's parity flips
                self.bx[k] ^= x
                self._fenx(self.fx, k, x)
            if old + c:
                self.cnt[x ^ self.salt if x.__class__ is int else x] = old + c
                self.cnts[k][j] += c
                self.bc[k] += c
                self._fen(self.fc, k, c)
                return old + c
            del self.cnt[x ^ self.salt if x.__class__ is int else x]
            self.d -= 1
            self.due -= 1
            del self.keys[k][j], self.cnts[k][j]
            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.maxes[k], self.bc[k]
                del self.bx[k]
                del self.bo[k]
                self.fc = None
                self.fx = None
                return 0
            self.maxes[k] = self.keys[k][-1]
            self.bo[k] = reduce(or_, self.keys[k], 0)  # x left: the block's OR / AND again
            self.bc[k] += c
            self._fen(self.fc, k, c)
            if len(self.keys) > 2 * self.d // self.load + 2:  # too many blocks for the values: cut again
                self._recut()
            return 0
        self.cnt[x ^ self.salt if x.__class__ is int else x] = c
        self.d += 1
        self.due -= 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
            self.maxes.append(x)
            self.bc.append(c)
            self.bx.append(x if c & 1 else 0)
            self.bo.append(x)
            self.fc = None
            self.fx = None
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
        if c & 1:
            self.bx[k] ^= x
            self._fenx(self.fx, k, x)
        self.bo[k] |= x
        if len(self.keys[k]) > 2 * self.load:  # split the block in half
            h = self.load
            for arr in (self.keys, self.cnts):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
            self.bx[k:k + 1] = [self._xodd(self.keys[k], self.cnts[k]), self._xodd(self.keys[k + 1], self.cnts[k + 1])]
            self.bo[k:k + 1] = [reduce(or_, self.keys[k], 0), reduce(or_, self.keys[k + 1], 0)]
            self.fc = None
            self.fx = None
            if len(self.keys) > 2 * self.d // self.load + 2:  # too many blocks for the values: cut again
                self._recut()
        return c

    def _recut(self):  # every block cut again at sqrt(N) / 8: O(N), at most once per N / 4 value adds / drops
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
        self.maxes = [b[-1] for b in self.keys]
        self.bc = list(map(sum, self.cnts))
        self.bx = list(map(self._xodd, self.keys, self.cnts))
        self.bo = [reduce(or_, b, 0) for b in self.keys]
        self.fc = None
        self.fx = None

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
        return self.cnt.get(x ^ self.salt if x.__class__ is int else x, 0)

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

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps both medians, the mex current
        self.n += c
        if c & 1:  # an odd number of copies flips x in or out of the xor of everything
            self.xtotal ^= x
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
                self.lowV = self.highV = x
                self.lowB = self.highB = 0
                self.lowC = self.highC = c
                return
        else:
            if 0 <= x < self.mexV and not f:  # the last copy of a value below the mex
                self.mexV = x
            if not n:
                return
        # each median is a tracked rank: shift its (value, copies before, copies), and search again only when the rank
        # leaves the tracked value
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

    def _swapFreq(self, old, new):
        # in the max-heap of counts, count old (0: none) becomes count new (0: none), O(log N)
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
        self.xtotal = 0

    def _clearData(self):
        self.keys, self.cnts, self.maxes, self.bc = [], [], [], []
        self.fc = None
        self.load, self.due = self.LOAD, self.LOAD * self.LOAD >> 1
        self.cnt = {}
        self.bx, self.fx = [], None
        self.bo = []

    def _distinctLt(self, x):  # distinct values < x: every block before x's, then a binary search in x's block
        keys = self.keys
        b = bisect_left(self.maxes, x)
        return sum(map(len, keys[:b])) + (bisect_left(keys[b], x) if b < len(keys) else 0)

    @staticmethod
    def _buildx(a):  # xor Fenwick over a
        f = [0] + a
        for i in range(1, len(f)):
            j = i + (i & -i)
            if j < len(f):
                f[j] ^= f[i]
        return f

    @staticmethod
    def _fenx(f, i, v):
        if f is not None:
            i += 1
            while i < len(f):
                f[i] ^= v
                i += i & -i

    def _xpre(self, k):  # xor of blocks 0..k-1
        f = self.fx
        if f is None:
            f = self.fx = self._buildx(self.bx)
        res = 0
        while k > 0:
            res ^= f[k]
            k &= k - 1
        return res

    @staticmethod
    def _xodd(keys, cnts):  # xor of the values with an odd count
        return reduce(xor, compress(keys, map(and_, cnts, repeat(1))), 0)

    def _xbelow(self, x, strict):  # xor of the values < x (strict) or <= x (copies count)
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.xtotal
        j = (bisect_left if strict else bisect_right)(self.keys[k], x)
        return self._xpre(k) ^ self._xodd(self.keys[k][:j], self.cnts[k][:j])

    def _xlt(self, x):
        return self._xbelow(x, True)

    def _xle(self, x):
        return self._xbelow(x, False)

    def _xorFirst(self, k):  # xor of the k smallest values (copies count)
        if k <= 0:
            return 0
        b, before, _ = self._locate(k)
        cn = self.cnts[b]
        pre = list(accumulate(cn))
        j = bisect_left(pre, k - before)
        res = self._xpre(b) ^ self._xodd(self.keys[b][:j], cn[:j])
        return res ^ self.keys[b][j] if (k - before - pre[j] + cn[j]) & 1 else res  # (copies of the k-th taken)

    def _orLe(self, x):  # OR of the values <= x
        b = bisect_right(self.maxes, x)  # blocks before b hold only values <= x
        res = reduce(or_, self.bo[:b], 0)
        if b < len(self.keys):
            blk = self.keys[b]
            res = reduce(or_, blk[:bisect_right(blk, x)], res)
        return res

    def _orGe(self, x):  # OR of the values >= x
        a = bisect_left(self.maxes, x)  # blocks after a hold only values >= x
        if a == len(self.keys):
            return 0
        blk = self.keys[a]
        return reduce(or_, self.bo[a + 1:], reduce(or_, blk[bisect_left(blk, x):], 0))

    def _orIn(self, lo, hi):  # OR of the values in [lo, hi] (lo <= hi)
        keys = self.keys
        a, b = bisect_left(self.maxes, lo), bisect_right(self.maxes, hi)
        if a == len(keys):
            return 0
        blk = keys[a]
        i = bisect_left(blk, lo)
        if a == b:  # one block holds them all
            return reduce(or_, blk[i:bisect_right(blk, hi)], 0)
        res = reduce(or_, self.bo[a + 1:b], reduce(or_, blk[i:], 0))  # blocks a + 1 .. b - 1 lie wholly inside
        if b < len(keys):
            res = reduce(or_, keys[b][:bisect_right(keys[b], hi)], res)
        return res

    # O(sqrtN amortized) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(sqrtN amortized) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1 amortized) -- remove everything (fine on an empty set): afterwards it is as if newly built (same constructor
    # arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logN) -- how many copies of x (0 if x isn't there, e.g. on an empty set)
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values (0 if empty)
    def countDistinct(self):
        return self.d

    # O(sqrtN) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    def countDistinctInValRange(self, lo, hi):
        if lo > hi:
            return 0
        return self._distinctLt(hi) - self._distinctLt(lo) + (1 if self._countOf(hi) else 0)

    # O(sqrtN) -- how many values > x (0 if there are none, e.g. on an empty set)
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(sqrtN) -- how many values >= x (0 if there are none, e.g. on an empty set)
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(sqrtN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(sqrtN) -- how many values < x (0 if there are none, e.g. on an empty set)
    def countLtX(self, x):
        return self._lt(x)

    # O(sqrtN) -- how many values <= x (0 if there are none, e.g. on an empty set)
    def countLteX(self, x):
        return self._le(x)

    # O(sqrtN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in
    # the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(sqrtN) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    # kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1)

    # O(sqrtN) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(sqrtN) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        c = self._le(x)
        return self._kth(c) if c else None

    # O(sqrtN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is
    # not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(sqrtN) -- largest value; raises IndexError if empty
    def max(self):
        if not self.n:
            raise IndexError("max: the set is empty")
        return self._kth(self.n)

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

    # O(1) -- smallest non-negative integer not in the set (0 if empty)
    def mex(self):
        return self.mexV

    # O(sqrtN) -- smallest value; raises IndexError if empty
    def min(self):
        if not self.n:
            raise IndexError("min: the set is empty")
        return self._kth(1)

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

    # O(sqrtN) -- bitwise OR of all values; 0 if empty
    def orOfAll(self):
        return reduce(or_, self.bo, 0)

    # O(sqrtN) -- bitwise OR of the values > x; 0 if there are none
    def orOfGtX(self, x):
        return self._orGe(x + 1)

    # O(sqrtN) -- bitwise OR of the values >= x; 0 if there are none
    def orOfGteX(self, x):
        return self._orGe(x)

    # O(sqrtN) -- bitwise OR of the values v with lo <= v <= hi; 0 if there are none
    def orOfInValRange(self, lo, hi):
        return self._orIn(lo, hi) if lo <= hi else 0

    # O(sqrtN) -- bitwise OR of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._orIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(sqrtN) -- bitwise OR of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError
    # unless 1 <= kFrom <= kTo <= size
    def orOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._orIn(self._kth(kFrom), self._kth(kTo))

    # O(sqrtN) -- bitwise OR of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k =
    # 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); raises IndexError
    # unless 0 <= k <= size
    def orOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orGe(self._kth(self.n - k + 1)) if k else 0

    # O(sqrtN) -- bitwise OR of the values < x; 0 if there are none
    def orOfLtX(self, x):
        return self._orLe(x - 1)

    # O(sqrtN) -- bitwise OR of the values <= x; 0 if there are none
    def orOfLteX(self, x):
        return self._orLe(x)

    # O(sqrtN) -- bitwise OR of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k
    # = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); raises IndexError
    # unless 0 <= k <= size
    def orOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orLe(self._kth(k)) if k else 0

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
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(sqrtN amortized) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self._kth(1)
        self._add(v, -1)
        return v

    # O(sqrtN amortized) -- remove one copy of x if present; returns how many were removed (0 or 1: 0 if x isn't there,
    # e.g. on an empty set)
    def remove(self, x):
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(sqrtN amortized) -- remove every copy of val; returns how many were removed (0 if val isn't there, e.g. on an
    # empty set)
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(sqrtN amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed (0 if val isn't
    # there, e.g. on an empty set)
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

    # O(1) -- how many values (copies count; 0 if empty)
    def size(self):
        return self.n

    # O(1) -- same as size()
    def __len__(self):
        return self.n

    # O(sqrtN) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(sqrtN) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None

    # O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    def xorOfAll(self):
        return self.xtotal

    # O(sqrtN) -- xor of the values > x (copies count; 0 if there are none)
    def xorOfGtX(self, x):
        return self.xtotal ^ self._xle(x)

    # O(sqrtN) -- xor of the values >= x (copies count; 0 if there are none)
    def xorOfGteX(self, x):
        return self.xtotal ^ self._xlt(x)

    # O(sqrtN) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    def xorOfInValRange(self, lo, hi):
        return self._xle(hi) ^ self._xlt(lo) if lo <= hi else 0

    # O(sqrtN) -- xor of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    # largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises IndexError unless
    # 1 <= kFrom <= kTo <= size
    def xorOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._xorFirst(self.n - kFrom + 1) ^ self._xorFirst(self.n - kTo)

    # O(sqrtN) -- xor of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    # smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError unless 1
    # <= kFrom <= kTo <= size
    def xorOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._xorFirst(kTo) ^ self._xorFirst(kFrom - 1)

    # O(sqrtN) -- xor of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    # the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); raises IndexError unless 0 <=
    # k <= size
    def xorOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.xtotal ^ self._xorFirst(self.n - k)

    # O(sqrtN) -- xor of the values < x (copies count; 0 if there are none)
    def xorOfLtX(self, x):
        return self._xlt(x)

    # O(sqrtN) -- xor of the values <= x (copies count; 0 if there are none)
    def xorOfLteX(self, x):
        return self._xle(x)

    # O(sqrtN) -- xor of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1
    # just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); raises IndexError
    # unless 0 <= k <= size
    def xorOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._xorFirst(k)
