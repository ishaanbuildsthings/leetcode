# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/blocks-with-gcd-lcm/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex gcdOfAll gcdOfGtX gcdOfGteX gcdOfInValRange gcdOfKthLargestRange gcdOfKthSmallestRange gcdOfLargestK gcdOfLtX gcdOfLteX gcdOfSmallestK kth largestLtX largestLteX lastIndex lcmOfAll lcmOfGtX lcmOfGteX lcmOfInValRange lcmOfKthLargestRange lcmOfKthSmallestRange lcmOfLargestK lcmOfLtX lcmOfLteX lcmOfSmallestK max medianHigh medianLow mex min pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
# @data-structure-type: blocks
# @values: online
# @keys: numbers
# @tracks: none
# @complexities:
#   add: sqrt(N)*log(U) amortized
#   addCount: sqrt(N)*log(U) amortized
#   lcmOfAll: sqrt(N)*log(U)
#   lcmOfGtX: sqrt(N)*log(U)
#   lcmOfGteX: sqrt(N)*log(U)
#   lcmOfInValRange: sqrt(N)*log(U)
#   lcmOfKthLargestRange: sqrt(N)*log(U)
#   lcmOfKthSmallestRange: sqrt(N)*log(U)
#   lcmOfLargestK: sqrt(N)*log(U)
#   lcmOfLtX: sqrt(N)*log(U)
#   lcmOfLteX: sqrt(N)*log(U)
#   lcmOfSmallestK: sqrt(N)*log(U)
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
#   medianHigh: sqrt(N)
#   medianLow: sqrt(N)
#   mex: sqrt(N)
#   min: sqrt(N)
#   gcdOfAll: sqrt(N)*log(U)
#   gcdOfGtX: sqrt(N)*log(U)
#   gcdOfGteX: sqrt(N)*log(U)
#   gcdOfInValRange: sqrt(N)*log(U)
#   gcdOfKthLargestRange: sqrt(N)*log(U)
#   gcdOfKthSmallestRange: sqrt(N)*log(U)
#   gcdOfLargestK: sqrt(N)*log(U)
#   gcdOfLtX: sqrt(N)*log(U)
#   gcdOfLteX: sqrt(N)*log(U)
#   gcdOfSmallestK: sqrt(N)*log(U)
#   pop: sqrt(N)*log(U) amortized
#   popMax: sqrt(N)*log(U) amortized
#   popMin: sqrt(N)*log(U) amortized
#   remove: sqrt(N)*log(U) amortized
#   removeAll: sqrt(N)*log(U) amortized
#   removeCount: sqrt(N)*log(U) amortized
#   removeInValRange: sqrt(N)*log(U) amortized
#   size: 1
#   smallestGtX: sqrt(N)
#   smallestGteX: sqrt(N)
#   build: 1
# @memory:
#   layout: none
#   node: keys[1*N] cnts[1*N]
#   tags: none
#   other: maxes[20*sqrt(N)+2] bc[40*sqrt(N)+5] bg[20*sqrt(N)+2] bm[20*sqrt(N)+2] cnt[1*N]
#   note: N = distinct values present; blocks of max(LOAD, sqrt(N) / 8) values (LOAD: Python 64, C++ 512), all cut again once N / 2 distinct values have come or gone, or once there are more than 2 * N / size + 2 blocks; each operation costs a few binary searches plus one block's worth of C-level list work
# lcmOf... answers -1 once the LCM passes cap, so it never overflows: cap is a constructor argument, the largest
# value (2**63 - 1) by default; pass your own, e.g. BlockMultiset(cap=10**9). Removing values is safe: every node
# keeps the capped LCM of just its own values, so once the values that pushed it past cap are gone, lcmOf... is exact
# again. Values must be >= 0. An empty selection gives the identity: gcd 0, LCM 1.
from math import gcd
from random import getrandbits
from bisect import bisect_left, bisect_right, insort
from functools import reduce
from itertools import accumulate, chain
from math import isqrt


# Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
# max(LOAD, sqrt(N) / 8), each block keeping its values' copies plus block totals and each block's gcd / LCM, and a
# Fenwick tree over the
# block totals (rebuilt only after a block splits or empties). A block splits in half past twice the block size, and
# once N / 2 distinct values have come or gone since the last cut, every block is cut again at that size: blocks
# follow sqrt(N) as N grows or shrinks (small blocks are faster in practice; any constant times sqrt(N) keeps the
# bounds). The blocks are also cut again as soon as there are more than 2 * N / size + 2 of them (removals can leave
# many small blocks), so there are never more than 20 sqrt(N) + 2. A cut is O(N), paid for by the N / 4 or more
# updates since the last one. A query
# finds its block by binary search (or by lifting over the block Fenwick for k-th) and then works inside one block
# with C-level list operations.


class BlockMultiset:
    LOAD = 64  # the smallest block size (sqrt(N) / 8 once N passes (8 * LOAD)^2)
    __slots__ = ("load", "due", "keys", "cnts", "maxes", "bc", "fc", "bg", "bm", "cnt", "n", "salt", "d", "cap")

    # O(1) -- an empty multiset
    def __init__(self, cap=2**63 - 1):
        self.cap = cap
        self.keys = []  # blocks of sorted distinct values
        self.cnts = []  # per block: copies of each value
        self.maxes = []  # last value of each block
        self.bc = []  # per block: total copies
        self.fc = None  # Fenwick over bc (None: stale)
        self.bg = []  # per block: gcd of its values
        self.bm = []  # per block: capped LCM of its values
        self.cnt = {}  # value -> copies
        # block size; distinct values to add / drop before a cut
        self.load, self.due = self.LOAD, self.LOAD * self.LOAD >> 1
        self.salt = getrandbits(60)  # hash containers key on salted values, so no fixed input can force collisions
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
                del self.bg[k]
                del self.bm[k]
                self.fc = None
                return 0
            self.maxes[k] = self.keys[k][-1]
            self.bg[k] = reduce(gcd, self.keys[k], 0)  # x left: the block's gcd / LCM again
            self.bm[k] = reduce(self._lc, self.keys[k], 1)
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
            self.bg.append(x)
            self.bm.append(self._lc(1, x))
            self.fc = None
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
        self.bg[k] = gcd(self.bg[k], x)
        self.bm[k] = self._lc(self.bm[k], x)
        if len(self.keys[k]) > 2 * self.load:  # split the block in half
            h = self.load
            for arr in (self.keys, self.cnts):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
            self.bg[k:k + 1] = [reduce(gcd, self.keys[k], 0), reduce(gcd, self.keys[k + 1], 0)]
            self.bm[k:k + 1] = [reduce(self._lc, self.keys[k], 1), reduce(self._lc, self.keys[k + 1], 1)]
            self.fc = None
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
        self.bg = [reduce(gcd, b, 0) for b in self.keys]
        self.bm = [reduce(self._lc, b, 1) for b in self.keys]
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

    def _add(self, x, c):  # c copies of x (c < 0 removes)
        self.n += c
        self._insert(x, c)

    def _resetCached(self):  # nothing counted: as newly built
        self.n = self.d = 0

    def _clearData(self):
        self.keys, self.cnts, self.maxes, self.bc = [], [], [], []
        self.fc = None
        self.load, self.due = self.LOAD, self.LOAD * self.LOAD >> 1
        self.cnt = {}
        self.bg = []
        self.bm = []

    def _distinctLt(self, x):  # distinct values < x: every block before x's, then a binary search in x's block
        keys = self.keys
        b = bisect_left(self.maxes, x)
        return sum(map(len, keys[:b])) + (bisect_left(keys[b], x) if b < len(keys) else 0)

    def _gcdLe(self, x):  # gcd of the values <= x
        b = bisect_right(self.maxes, x)  # blocks before b hold only values <= x
        res = reduce(gcd, self.bg[:b], 0)
        if b < len(self.keys):
            blk = self.keys[b]
            res = reduce(gcd, blk[:bisect_right(blk, x)], res)
        return res

    def _gcdGe(self, x):  # gcd of the values >= x
        a = bisect_left(self.maxes, x)  # blocks after a hold only values >= x
        if a == len(self.keys):
            return 0
        blk = self.keys[a]
        return reduce(gcd, self.bg[a + 1:], reduce(gcd, blk[bisect_left(blk, x):], 0))

    def _gcdIn(self, lo, hi):  # gcd of the values in [lo, hi] (lo <= hi)
        keys = self.keys
        a, b = bisect_left(self.maxes, lo), bisect_right(self.maxes, hi)
        if a == len(keys):
            return 0
        blk = keys[a]
        i = bisect_left(blk, lo)
        if a == b:  # one block holds them all
            return reduce(gcd, blk[i:bisect_right(blk, hi)], 0)
        res = reduce(gcd, self.bg[a + 1:b], reduce(gcd, blk[i:], 0))  # blocks a + 1 .. b - 1 lie wholly inside
        if b < len(keys):
            res = reduce(gcd, keys[b][:bisect_right(keys[b], hi)], res)
        return res

    def _lcmLe(self, x):  # capped LCM of the values <= x
        b = bisect_right(self.maxes, x)  # blocks before b hold only values <= x
        res = reduce(self._lc, self.bm[:b], 1)
        if b < len(self.keys):
            blk = self.keys[b]
            res = reduce(self._lc, blk[:bisect_right(blk, x)], res)
        return res

    def _lcmGe(self, x):  # capped LCM of the values >= x
        a = bisect_left(self.maxes, x)  # blocks after a hold only values >= x
        if a == len(self.keys):
            return 1
        blk = self.keys[a]
        return reduce(self._lc, self.bm[a + 1:], reduce(self._lc, blk[bisect_left(blk, x):], 1))

    def _lcmIn(self, lo, hi):  # capped LCM of the values in [lo, hi] (lo <= hi)
        keys = self.keys
        a, b = bisect_left(self.maxes, lo), bisect_right(self.maxes, hi)
        if a == len(keys):
            return 1
        blk = keys[a]
        i = bisect_left(blk, lo)
        if a == b:  # one block holds them all
            return reduce(self._lc, blk[i:bisect_right(blk, hi)], 1)
        # blocks a + 1 .. b - 1 lie wholly inside
        res = reduce(self._lc, self.bm[a + 1:b], reduce(self._lc, blk[i:], 1))
        if b < len(keys):
            res = reduce(self._lc, keys[b][:bisect_right(keys[b], hi)], res)
        return res

    # O(sqrtN * logU amortized) -- add one copy of x
    def add(self, x):
        self.n += 1
        self._insert(x, 1)

    # O(sqrtN * logU amortized) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(sqrtN * logU) -- LCM (-1 once it passes cap) of all values; 1 if empty
    def lcmOfAll(self):
        return reduce(self._lc, self.bm, 1)

    # O(sqrtN * logU) -- LCM (-1 once it passes cap) of the values > x; 1 if there are none
    def lcmOfGtX(self, x):
        return self._lcmGe(x + 1)

    # O(sqrtN * logU) -- LCM (-1 once it passes cap) of the values >= x; 1 if there are none
    def lcmOfGteX(self, x):
        return self._lcmGe(x)

    # O(sqrtN * logU) -- LCM (-1 once it passes cap) of the values v with lo <= v <= hi; 1 if there are none
    def lcmOfInValRange(self, lo, hi):
        return self._lcmIn(lo, hi) if lo <= hi else 1

    # O(sqrtN * logU) -- LCM (-1 once it passes cap) of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and
    # inclusive: (1, 1) is
    # just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def lcmOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"lcmOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._lcmIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(sqrtN * logU) -- LCM (-1 once it passes cap) of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed
    # and inclusive: (1, 1) is
    # just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError
    # unless 1 <= kFrom <= kTo <= size
    def lcmOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"lcmOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._lcmIn(self._kth(kFrom), self._kth(kTo))

    # O(sqrtN * logU) -- LCM (-1 once it passes cap) of the k largest values; k is a COUNT, not an index: k = 0 takes no
    # values (returns 1),
    # k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    # raises IndexError unless 0 <= k <= size
    def lcmOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"lcmOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._lcmGe(self._kth(self.n - k + 1)) if k else 1

    # O(sqrtN * logU) -- LCM (-1 once it passes cap) of the values < x; 1 if there are none
    def lcmOfLtX(self, x):
        return self._lcmLe(x - 1)

    # O(sqrtN * logU) -- LCM (-1 once it passes cap) of the values <= x; 1 if there are none
    def lcmOfLteX(self, x):
        return self._lcmLe(x)

    # O(sqrtN * logU) -- LCM (-1 once it passes cap) of the k smallest values; k is a COUNT, not an index: k = 0 takes
    # no values (returns 1),
    # k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
    # raises IndexError unless 0 <= k <= size
    def lcmOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"lcmOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._lcmLe(self._kth(k)) if k else 1

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

    # O(sqrtN) -- upper median: the (floor(size/2) + 1)-th smallest value; raises IndexError if empty
    def medianHigh(self):
        if not self.n:
            raise IndexError("medianHigh: the set is empty")
        return self._kth((self.n >> 1) + 1)

    # O(sqrtN) -- lower median: the ceil(size/2)-th smallest value; raises IndexError if empty
    def medianLow(self):
        if not self.n:
            raise IndexError("medianLow: the set is empty")
        return self._kth((self.n + 1) >> 1)

    # O(sqrtN) -- smallest non-negative integer not in the set (0 if empty)
    def mex(self):
        return self._findMex()

    # O(sqrtN) -- smallest value; raises IndexError if empty
    def min(self):
        if not self.n:
            raise IndexError("min: the set is empty")
        return self._kth(1)

    # O(sqrtN * logU) -- gcd of all values; 0 if empty
    def gcdOfAll(self):
        return reduce(gcd, self.bg, 0)

    # O(sqrtN * logU) -- gcd of the values > x; 0 if there are none
    def gcdOfGtX(self, x):
        return self._gcdGe(x + 1)

    # O(sqrtN * logU) -- gcd of the values >= x; 0 if there are none
    def gcdOfGteX(self, x):
        return self._gcdGe(x)

    # O(sqrtN * logU) -- gcd of the values v with lo <= v <= hi; 0 if there are none
    def gcdOfInValRange(self, lo, hi):
        return self._gcdIn(lo, hi) if lo <= hi else 0

    # O(sqrtN * logU) -- gcd of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def gcdOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"gcdOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._gcdIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(sqrtN * logU) -- gcd of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError
    # unless 1 <= kFrom <= kTo <= size
    def gcdOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"gcdOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._gcdIn(self._kth(kFrom), self._kth(kTo))

    # O(sqrtN * logU) -- gcd of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k =
    # 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); raises IndexError
    # unless 0 <= k <= size
    def gcdOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"gcdOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._gcdGe(self._kth(self.n - k + 1)) if k else 0

    # O(sqrtN * logU) -- gcd of the values < x; 0 if there are none
    def gcdOfLtX(self, x):
        return self._gcdLe(x - 1)

    # O(sqrtN * logU) -- gcd of the values <= x; 0 if there are none
    def gcdOfLteX(self, x):
        return self._gcdLe(x)

    # O(sqrtN * logU) -- gcd of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k
    # = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); raises IndexError
    # unless 0 <= k <= size
    def gcdOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"gcdOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._gcdLe(self._kth(k)) if k else 0

    # O(sqrtN * logU amortized) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the
    # smallest (=
    # popMin()), pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(sqrtN * logU amortized) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(sqrtN * logU amortized) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self._kth(1)
        self._add(v, -1)
        return v

    # O(sqrtN * logU amortized) -- remove one copy of x if present; returns how many were removed (0 or 1: 0 if x isn't
    # there,
    # e.g. on an empty set)
    def remove(self, x):
        if not self._countOf(x):
            return 0
        self.n -= 1
        self._insert(x, -1)
        return 1

    # O(sqrtN * logU amortized) -- remove every copy of val; returns how many were removed (0 if val isn't there, e.g.
    # on an
    # empty set)
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(sqrtN * logU amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed (0 if val
    # isn't
    # there, e.g. on an empty set)
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(sqrtN * logU amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if
    # lo > hi)
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

    def _lc(self, a, b):  # capped LCM: 0 if either is 0, else -1 if either is -1 (too big), else the LCM or -1 past cap
        if a == 0 or b == 0:
            return 0
        if a < 0 or b < 0:
            return -1
        r = a // gcd(a, b) * b
        return r if r <= self.cap else -1

