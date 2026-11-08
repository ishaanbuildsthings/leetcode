# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/fastset-with-minmax-mode-gaps/template.py
# @operations: add addCount clear count countDistinct largestLtX largestLteX max maxGap min minAdjacentDiff mode popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
# @data-structure-type: fastset
# @values: online-range
# @keys: numbers
# @tracks: minmax mode gaps
# @complexities:
#   add: log64(U) amortized
#   addCount: log64(U) amortized
#   clear: 1 amortized
#   count: 1
#   countDistinct: 1
#   largestLtX: log64(U)
#   largestLteX: log64(U)
#   max: 1
#   maxGap: 1 amortized
#   min: 1
#   minAdjacentDiff: 1 amortized
#   mode: 1
#   popMax: log64(U) amortized
#   popMin: log64(U) amortized
#   remove: log64(U) amortized
#   removeAll: log64(U) amortized
#   removeCount: log64(U) amortized
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
from random import getrandbits
from heapq import heappop, heappush

# Ordered multiset of integers in [lo, hi] (FastSet): a 64-ary bit trie over the U = hi - lo + 1 slots, a bit meaning
# "this value (or something under this word) is present", plus a count per value. add / remove / smallest >= x /
# largest <= x touch one word per level: log_64(U) levels, about 4 for U = 10^7. It keeps no ranks, so no k-th and
# no "how many below x".


class FastSetMultiset:
    __slots__ = ("lo", "hi", "u", "seg", "cnt", "n", "mn", "mx", "bk", "bkAt", "fh", "fhAt", "gc", "gmin", "gmax", "dups", "salt", "d")

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
        self.salt = getrandbits(60)  # hash containers key on salted values, so no fixed input can force collisions
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.bk, self.bkAt = {}, {}  # mode: count -> list of the values with that many copies; value -> its index there
        self.fh, self.fhAt = [], {}  # mode: max-heap of the counts that have a bucket; count -> its index in it
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

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max current
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
        self.bk, self.bkAt, self.fh, self.fhAt = {}, {}, [], {}
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

    # O(log64(U) amortized) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(log64(U) amortized) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    # instead of building a new one
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

    # O(1) -- largest value; raises IndexError if empty
    def max(self):
        if not self.n:
            raise IndexError("max: the set is empty")
        return self.mx

    # O(1 amortized) -- largest difference between two neighbouring distinct values; None if fewer than 2 distinct
    # values
    def maxGap(self):
        return self._maxGap() if self.d >= 2 else None

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

    # O(log64(U) amortized) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self.mx
        self._add(v, -1)
        return v

    # O(log64(U) amortized) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self.mn
        self._add(v, -1)
        return v

    # O(log64(U) amortized) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(log64(U) amortized) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(log64(U) amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(log64(U) amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed
    # (0 if lo > hi)
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
