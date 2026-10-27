# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/fastset-with-gaps/distinct.py
# @operations: add clear count countDistinct largestLtX largestLteX max maxGap min minAdjacentDiff popMax popMin remove removeInValRange size smallestGtX smallestGteX
# @data-structure-type: fastset
# @values: online-range
# @keys: numbers
# @tracks: gaps
# @complexities:
#   add: log64(U)
#   clear: N*log64(U)
#   count: 1
#   countDistinct: 1
#   largestLtX: log64(U)
#   largestLteX: log64(U)
#   max: log64(U)
#   maxGap: 1 amortized
#   min: log64(U)
#   minAdjacentDiff: 1 amortized
#   popMax: log64(U)
#   popMin: log64(U)
#   remove: log64(U)
#   removeInValRange: log64(U) amortized
#   size: 1
#   smallestGtX: log64(U)
#   smallestGteX: log64(U)
#   build: U/64
# @memory:
#   layout: none
#   node: seg[1*U/64]
#   tags: none
#   other: none
#   note: U = hi - lo + 1: just the trie's U / 64 + U / 4096 + ... 64-bit words (about U / 63); no duplicates
from heapq import heappop, heappush

# Ordered set of DISTINCT integers in [lo, hi] (FastSet): a 64-ary bit trie over the U = hi - lo + 1 slots, a bit
# meaning "this value (or something under this word) is present". No duplicates: adding a value that is already in
# the set does nothing, so there is no count per value and building is just the trie's ~U / 63 words. Every op touches
# one word per level: log_64(U) levels, about 4 for U = 10^7.


class FastSet:
    __slots__ = ("lo", "hi", "u", "seg", "n", "gc", "gmin", "gmax")

    # O(U/64) -- lo, hi: every value added lies in [lo, hi] (any integers, negative is fine); U = hi - lo + 1
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        u = self.u = hi - lo + 1
        self.seg = []  # seg[h][w] = 64 bits, one per word of level h - 1 (level 0: one per value)
        width = max(u, 1)
        while True:
            words = (width + 63) >> 6
            self.seg.append([0] * words)
            if words == 1:
                break
            width = words
        self.n = 0
        self.gc, self.gmin, self.gmax = {}, [], []  # gaps: size -> how many; min / max heaps

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

    # O(log64(U)) -- add x (nothing if x is already in the set: no duplicates)
    def add(self, x):
        i = x - self.lo  # x must lie in [lo, hi]
        seg = self.seg
        if (seg[0][i >> 6] >> (i & 63)) & 1:
            return
        self.n += 1
        p, q = self._prev(i - 1), self._next(i + 1)  # gaps: x splits the gap between its neighbours
        if p >= 0 and q >= 0:
            self._gap(q - p, -1)
        if p >= 0:
            self._gap(i - p, 1)
        if q >= 0:
            self._gap(q - i, 1)
        for level in seg:
            level[i >> 6] |= 1 << (i & 63)
            i >>= 6

    # O(log64(U)) -- remove x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        i = x - self.lo
        if not 0 <= i < self.u or not (self.seg[0][i >> 6] >> (i & 63)) & 1:
            return 0
        self.n -= 1
        for level in self.seg:
            j = i >> 6
            w = level[j] & ~(1 << (i & 63))
            level[j] = w
            if w:
                break
            i = j
        k = x - self.lo
        p, q = self._prev(k - 1), self._next(k + 1)  # gaps: the gap between x's neighbours comes back
        if p >= 0:
            self._gap(k - p, -1)
        if q >= 0:
            self._gap(q - k, -1)
        if p >= 0 and q >= 0:
            self._gap(q - p, 1)
        return 1

    # O(N log64(U)) -- remove everything (N = values in it): as newly built, so reuse it instead of building a new one
    def clear(self):
        self.n = 0
        self.gc, self.gmin, self.gmax = {}, [], []
        self._clearWords()

    def _clearWords(self):  # zero only the trie words in use (walking down from the top through set bits)
        seg = self.seg
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

    # O(log64(U) amortized) -- remove every value v with lo <= v <= hi; returns how many were removed (0 if lo > hi)
    def removeInValRange(self, lo, hi):
        if lo > hi:
            return 0
        removed = 0
        i = self._next(lo - self.lo)
        while i >= 0 and self.lo + i <= hi:
            self.remove(self.lo + i)
            removed += 1
            i = self._next(i + 1)
        return removed

    # O(1) -- 1 if x is in the set, else 0
    def count(self, x):
        i = x - self.lo
        return (self.seg[0][i >> 6] >> (i & 63)) & 1 if 0 <= i < self.u else 0

    # O(1) -- how many values (no duplicates, so also how many distinct)
    def countDistinct(self):
        return self.n

    # O(1) -- how many values
    def size(self):
        return self.n

    # O(1) -- same as size()
    def __len__(self):
        return self.n

    # O(log64(U)) -- smallest value; None if empty
    def min(self):
        i = self._next(0)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- largest value; None if empty
    def max(self):
        i = self._prev(self.u - 1)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- remove and return the smallest value; None if empty
    def popMin(self):
        v = self.min()
        if v is not None:
            self.remove(v)
        return v

    # O(log64(U)) -- remove and return the largest value; None if empty
    def popMax(self):
        v = self.max()
        if v is not None:
            self.remove(v)
        return v

    # O(log64(U)) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        i = self._next(x - self.lo)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        i = self._next(x - self.lo + 1)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        i = self._prev(x - self.lo)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- largest value < x; None if there is none
    def largestLtX(self, x):
        i = self._prev(x - self.lo - 1)
        return None if i < 0 else self.lo + i

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

    # O(1 amortized) -- smallest difference between two values in the set; None if fewer than 2 values
    def minAdjacentDiff(self):
        if self.n < 2:
            return None
        h, gc = self.gmin, self.gc
        while h[0] not in gc:  # heap tops of sizes no longer present are dropped as they surface
            heappop(h)
        return h[0]

    # O(1 amortized) -- largest difference between two neighbouring values; None if fewer than 2 values
    def maxGap(self):
        if self.n < 2:
            return None
        h, gc = self.gmax, self.gc
        while -h[0] not in gc:
            heappop(h)
        return -h[0]
