# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/blocks-with-xor-or-and-cachedmex-medians-mode/template.py
# @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min mode orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
# @data-structure-type: blocks
# @values: online
# @keys: numbers
# @tracks: medians mex mode
# @complexities:
#   add: sqrt(N)
#   addCount: sqrt(N)
#   andOfAll: sqrt(N)
#   andOfGtX: sqrt(N)
#   andOfGteX: sqrt(N)
#   andOfInValRange: sqrt(N)
#   andOfKthLargestRange: sqrt(N)
#   andOfKthSmallestRange: sqrt(N)
#   andOfLargestK: sqrt(N)
#   andOfLtX: sqrt(N)
#   andOfLteX: sqrt(N)
#   andOfSmallestK: sqrt(N)
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
#   max: sqrt(N)
#   medianHigh: 1
#   medianLow: 1
#   mex: 1
#   min: sqrt(N)
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
#   pop: sqrt(N)
#   popMax: sqrt(N)
#   popMin: sqrt(N)
#   remove: sqrt(N)
#   removeAll: sqrt(N)
#   removeCount: sqrt(N)
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
#   other: maxes[1*sqrt(N)] bc[2*sqrt(N)] bx[2*sqrt(N)] bo[1*sqrt(N)] ba[1*sqrt(N)] cnt[1*N]
#   note: N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); each operation costs a few binary searches plus one block's worth of C-level list work
from bisect import bisect_left, bisect_right, insort
from functools import reduce
from itertools import accumulate, compress, repeat
from operator import and_, or_, xor


# Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
# LOAD..2*LOAD, each block keeping its values' copies plus block totals and each block's xor / OR / AND, and a Fenwick tree over the
# block totals (rebuilt only after a block splits or empties). A query finds its block by binary search (or by
# lifting over the block Fenwick for k-th) and then works inside one block with C-level list operations.


class BlockMultiset:
    LOAD = 64
    __slots__ = ("keys", "cnts", "maxes", "bc", "fc", "bx", "fx", "bo", "ba", "cnt", "n", "lowV", "lowB", "lowC", "highV", "highB", "highC", "mexV", "bk", "maxF", "xtotal", "d")

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
        self.ba = []  # per block: AND of its values
        self.cnt = {}  # value -> copies
        self.xtotal = 0  # xor of all values (copies count)
        self.bk, self.maxF = {}, 0  # mode: count -> the values with that many copies; the highest count
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
        old = self.cnt.get(x, 0)
        if old:
            k = bisect_left(self.maxes, x)
            j = bisect_left(self.keys[k], x)
            if c & 1:  # x's parity flips
                self.bx[k] ^= x
                self._fenx(self.fx, k, x)
            if old + c:
                self.cnt[x] = old + c
                self.cnts[k][j] += c
                self.bc[k] += c
                self._fen(self.fc, k, c)
                return old + c
            del self.cnt[x]
            self.d -= 1
            del self.keys[k][j], self.cnts[k][j]
            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.maxes[k], self.bc[k]
                del self.bx[k]
                del self.bo[k]
                del self.ba[k]
                self.fc = None
                self.fx = None
                return 0
            self.maxes[k] = self.keys[k][-1]
            self.bo[k] = reduce(or_, self.keys[k], 0)  # x left: the block's OR / AND again
            self.ba[k] = reduce(and_, self.keys[k], -1)
            self.bc[k] += c
            self._fen(self.fc, k, c)
            return 0
        self.cnt[x] = c
        self.d += 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
            self.maxes.append(x)
            self.bc.append(c)
            self.bx.append(x if c & 1 else 0)
            self.bo.append(x)
            self.ba.append(x)
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
        self.ba[k] &= x
        if len(self.keys[k]) > 2 * self.LOAD:  # split the block in half
            h = self.LOAD
            for arr in (self.keys, self.cnts):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
            self.bx[k:k + 1] = [self._xodd(self.keys[k], self.cnts[k]), self._xodd(self.keys[k + 1], self.cnts[k + 1])]
            self.bo[k:k + 1] = [reduce(or_, self.keys[k], 0), reduce(or_, self.keys[k + 1], 0)]
            self.ba[k:k + 1] = [reduce(and_, self.keys[k], -1), reduce(and_, self.keys[k + 1], -1)]
            self.fc = None
            self.fx = None
        return c

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

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps both medians, the mex current
        self.n += c
        if c & 1:  # an odd number of copies flips x in or out of the xor of everything
            self.xtotal ^= x
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
        self.bk, self.maxF = {}, 0
        self.n = self.d = 0
        self.xtotal = 0

    def _clearData(self):
        self.keys, self.cnts, self.maxes, self.bc = [], [], [], []
        self.fc = None
        self.cnt = {}
        self.bx, self.fx = [], None
        self.bo = []
        self.ba = []

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

    def _andLe(self, x):  # AND of the values <= x
        b = bisect_right(self.maxes, x)  # blocks before b hold only values <= x
        res = reduce(and_, self.ba[:b], -1)
        if b < len(self.keys):
            blk = self.keys[b]
            res = reduce(and_, blk[:bisect_right(blk, x)], res)
        return res

    def _andGe(self, x):  # AND of the values >= x
        a = bisect_left(self.maxes, x)  # blocks after a hold only values >= x
        if a == len(self.keys):
            return -1
        blk = self.keys[a]
        return reduce(and_, self.ba[a + 1:], reduce(and_, blk[bisect_left(blk, x):], -1))

    def _andIn(self, lo, hi):  # AND of the values in [lo, hi] (lo <= hi)
        keys = self.keys
        a, b = bisect_left(self.maxes, lo), bisect_right(self.maxes, hi)
        if a == len(keys):
            return -1
        blk = keys[a]
        i = bisect_left(blk, lo)
        if a == b:  # one block holds them all
            return reduce(and_, blk[i:bisect_right(blk, hi)], -1)
        res = reduce(and_, self.ba[a + 1:b], reduce(and_, blk[i:], -1))  # blocks a + 1 .. b - 1 lie wholly inside
        if b < len(keys):
            res = reduce(and_, keys[b][:bisect_right(keys[b], hi)], res)
        return res

    # O(sqrtN) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(sqrtN) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(sqrtN) -- bitwise AND of all values; -1 (every bit set) if empty
    def andOfAll(self):
        return reduce(and_, self.ba, -1)

    # O(sqrtN) -- bitwise AND of the values > x; -1 (every bit set) if there are none
    def andOfGtX(self, x):
        return self._andGe(x + 1)

    # O(sqrtN) -- bitwise AND of the values >= x; -1 (every bit set) if there are none
    def andOfGteX(self, x):
        return self._andGe(x)

    # O(sqrtN) -- bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none
    def andOfInValRange(self, lo, hi):
        return self._andIn(lo, hi) if lo <= hi else -1

    # O(sqrtN) -- bitwise AND of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def andOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"andOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._andIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(sqrtN) -- bitwise AND of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def andOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"andOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._andIn(self._kth(kFrom), self._kth(kTo))

    # O(sqrtN) -- bitwise AND of the k largest values (-1 (every bit set) for k = 0); raises IndexError unless 0 <= k <= size
    def andOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"andOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._andGe(self._kth(self.n - k + 1)) if k else -1

    # O(sqrtN) -- bitwise AND of the values < x; -1 (every bit set) if there are none
    def andOfLtX(self, x):
        return self._andLe(x - 1)

    # O(sqrtN) -- bitwise AND of the values <= x; -1 (every bit set) if there are none
    def andOfLteX(self, x):
        return self._andLe(x)

    # O(sqrtN) -- bitwise AND of the k smallest values (-1 (every bit set) for k = 0); raises IndexError unless 0 <= k <= size
    def andOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"andOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._andLe(self._kth(k)) if k else -1

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

    # O(sqrtN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(sqrtN) -- the value at sorted position i (0-indexed: kth(0) is the min); raises IndexError unless 0 <= i < size
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

    # O(sqrtN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(sqrtN) -- largest value; None if empty
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

    # O(sqrtN) -- smallest value; None if empty
    def min(self):
        return self._kth(1) if self.n else None

    # O(1) -- (a most frequent value, its count); None if empty. C++ returns the smallest of the most frequent values
    def mode(self):
        if not self.n:
            return None
        f = self.maxF
        return next(iter(self.bk[f])), f

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

    # O(sqrtN) -- bitwise OR of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._orIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(sqrtN) -- bitwise OR of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._orIn(self._kth(kFrom), self._kth(kTo))

    # O(sqrtN) -- bitwise OR of the k largest values (0 for k = 0); raises IndexError unless 0 <= k <= size
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

    # O(sqrtN) -- bitwise OR of the k smallest values (0 for k = 0); raises IndexError unless 0 <= k <= size
    def orOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orLe(self._kth(k)) if k else 0

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

    # O(sqrtN) -- xor of the values > x (copies count)
    def xorOfGtX(self, x):
        return self.xtotal ^ self._xle(x)

    # O(sqrtN) -- xor of the values >= x (copies count)
    def xorOfGteX(self, x):
        return self.xtotal ^ self._xlt(x)

    # O(sqrtN) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    def xorOfInValRange(self, lo, hi):
        return self._xle(hi) ^ self._xlt(lo) if lo <= hi else 0

    # O(sqrtN) -- xor of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def xorOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._xorFirst(self.n - kFrom + 1) ^ self._xorFirst(self.n - kTo)

    # O(sqrtN) -- xor of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def xorOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._xorFirst(kTo) ^ self._xorFirst(kFrom - 1)

    # O(sqrtN) -- xor of the k largest values (copies count); raises IndexError unless 0 <= k <= size
    def xorOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.xtotal ^ self._xorFirst(self.n - k)

    # O(sqrtN) -- xor of the values < x (copies count)
    def xorOfLtX(self, x):
        return self._xlt(x)

    # O(sqrtN) -- xor of the values <= x (copies count)
    def xorOfLteX(self, x):
        return self._xle(x)

    # O(sqrtN) -- xor of the k smallest values (copies count); raises IndexError unless 0 <= k <= size
    def xorOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._xorFirst(k)
