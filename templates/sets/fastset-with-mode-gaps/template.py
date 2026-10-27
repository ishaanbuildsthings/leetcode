# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/fastset-with-mode-gaps/template.py
# @operations: add addCount clear count countDistinct largestLtX largestLteX max maxGap min minAdjacentDiff mode popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
# @data-structure-type: fastset
# @values: online-range
# @keys: numbers
# @tracks: mode gaps
# @complexities:
#   add: log64(U)
#   addCount: log64(U)
#   clear: N*log64(U)
#   count: 1
#   countDistinct: 1
#   largestLtX: log64(U)
#   largestLteX: log64(U)
#   max: log64(U)
#   maxGap: 1 amortized
#   min: log64(U)
#   minAdjacentDiff: 1 amortized
#   mode: 1
#   popMax: log64(U)
#   popMin: log64(U)
#   remove: log64(U)
#   removeAll: log64(U)
#   removeCount: log64(U)
#   removeInValRange: log64(U) amortized
#   size: 1
#   smallestGtX: log64(U)
#   smallestGteX: log64(U)
#   build: U
# @memory:
#   layout: none
#   node: cnt[1*U]
#   tags: none
#   other: none
#   note: U = hi - lo + 1: a count per value, plus the trie's U / 64 + U / 4096 + ... 64-bit words (about U / 63)
from heapq import heappop, heappush

# Ordered multiset of integers in [lo, hi] (FastSet): a 64-ary bit trie over the U = hi - lo + 1 slots, a bit meaning
# "this value (or something under this word) is present", plus a count per value. add / remove / smallest >= x /
# largest <= x touch one word per level: log_64(U) levels, about 4 for U = 10^7. It keeps no ranks, so no k-th and
# no "how many below x".


class FastSetMultiset:
    __slots__ = ("lo", "hi", "u", "seg", "cnt", "n", "bk", "maxF", "gc", "gmin", "gmax", "dups", "d")

    # O(U) -- lo, hi: every value added lies in [lo, hi] (any integers, negative is fine); U = hi - lo + 1
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        u = self.u = hi - lo + 1
        self.cnt = [0] * u  # copies of lo + i
        self.seg = []  # seg[h][w] = 64 bits, one per word of level h - 1 (level 0: one per value)
        width = max(u, 1)
        while True:
            words = (width + 63) >> 6
            self.seg.append([0] * words)
            if words == 1:
                break
            width = words
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.bk, self.maxF = {}, 0  # mode: count -> the values with that many copies; the highest count
        self.n = self.d = 0

    def _insert(self, x, c):
        i = x - self.lo  # x must lie in [lo, hi]
        old = self.cnt[i]
        new = self.cnt[i] = old + c
        if not old:  # first copy: set its bit on every level
            self.d += 1
            for level in self.seg:
                level[i >> 6] |= 1 << (i & 63)
                i >>= 6
        elif not new:  # last copy: clear bits upward while the word empties
            self.d -= 1
            for level in self.seg:
                j = i >> 6
                w = level[j] & ~(1 << (i & 63))
                level[j] = w
                if w:
                    break
                i = j
        return new

    def _countOf(self, x):
        return self.cnt[x - self.lo] if self.lo <= x <= self.hi else 0

    def _next(self, i):  # smallest present slot >= i, or -1
        if i < 0:
            i = 0
        if i >= self.u:
            return -1
        seg = self.seg
        for h in range(len(seg)):
            idx = i >> 6
            if idx >= len(seg[h]):
                break
            v = seg[h][idx] >> (i & 63)
            if v:
                i += (v & -v).bit_length() - 1
                for g in range(h - 1, -1, -1):
                    w = seg[g][i]
                    i = (i << 6) + (w & -w).bit_length() - 1
                return i
            i = idx + 1
        return -1

    def _prev(self, i):  # largest present slot <= i, or -1
        if i >= self.u:
            i = self.u - 1
        if i < 0:
            return -1
        seg = self.seg
        for h in range(len(seg)):
            idx = i >> 6
            v = seg[h][idx] & ((1 << ((i & 63) + 1)) - 1)
            if v:
                i = (idx << 6) + v.bit_length() - 1
                for g in range(h - 1, -1, -1):
                    i = (i << 6) + seg[g][i].bit_length() - 1
                return i
            if not idx:
                return -1
            i = idx - 1
        return -1

    def _kth(self, k):  # only the min (k = 1) or the max (k = n), for _add: the trie has no ranks
        return self.lo + (self._next(0) if k == 1 else self._prev(self.u - 1))

    def _add(self, x, c):  # c copies of x (c < 0 removes)
        self.n += c
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

    def _resetCached(self):  # nothing counted: as newly built
        self.bk, self.maxF = {}, 0
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0
        self.n = self.d = 0

    def _clearData(self):  # zero only the trie words in use (walking down from the top through set bits), and the counts of the values present
        seg, cnt = self.seg, self.cnt
        stack = [(len(seg) - 1, 0)]
        while stack:
            h, w = stack.pop()
            bits = seg[h][w]
            if not bits:
                continue
            seg[h][w] = 0
            base = w << 6
            while bits:
                b = (bits & -bits).bit_length() - 1
                bits &= bits - 1
                if h:
                    stack.append((h - 1, base + b))
                else:
                    cnt[base + b] = 0

    # O(log64(U)) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(log64(U)) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(N log64(U)) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(1) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(log64(U)) -- largest value < x; None if there is none
    def largestLtX(self, x):
        i = self._prev(x - self.lo - 1)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        i = self._prev(x - self.lo)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- largest value; None if empty
    def max(self):
        return self._kth(self.n) if self.n else None

    # O(1 amortized) -- largest difference between two neighbouring distinct values; None if fewer than 2 distinct values
    def maxGap(self):
        return self._maxGap() if self.d >= 2 else None

    # O(log64(U)) -- smallest value; None if empty
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

    # O(log64(U)) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(log64(U)) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self._kth(1)
        self._add(v, -1)
        return v

    # O(log64(U)) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self.count(x):
            return 0
        self._add(x, -1)
        return 1

    # O(log64(U)) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(log64(U)) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(log64(U) amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    def removeInValRange(self, lo, hi):
        if lo > hi:
            return 0
        removed = 0
        i = self._next(lo - self.lo)
        while i >= 0 and self.lo + i <= hi:  # each present value in [lo, hi]: drop all its copies
            k = self.cnt[i]
            self._add(self.lo + i, -k)
            removed += k
            i = self._next(i + 1)
        return removed

    # O(1) -- how many values (copies count)
    def size(self):
        return self.n

    # O(1) -- same as size()
    def __len__(self):
        return self.n

    # O(log64(U)) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        i = self._next(x - self.lo + 1)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        i = self._next(x - self.lo)
        return None if i < 0 else self.lo + i
