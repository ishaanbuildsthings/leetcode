# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/fastset/template.py
# @operations: add addCount clear count countDistinct largestLtX largestLteX max min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX
# @data-structure-type: fastset
# @values: online-range
# @keys: numbers
# @complexities:
#   add: log64(U)
#   addCount: log64(U)
#   clear: N*log64(U)
#   count: 1
#   countDistinct: 1
#   largestLtX: log64(U)
#   largestLteX: log64(U)
#   max: 1 amortized
#   min: 1 amortized
#   popMax: log64(U)
#   popMin: log64(U)
#   remove: log64(U)
#   removeAll: log64(U)
#   removeCount: log64(U)
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

# Ordered multiset of integers in [lo, hi] (FastSet): a 64-ary bit trie over the U = hi - lo + 1 slots, a bit meaning
# "this value (or something under this word) is present", plus a count per value. add / remove / smallest >= x /
# largest <= x touch one word per level: log_64(U) levels, about 4 for U = 10^7. It keeps no ranks, so no k-th and
# no "how many below x".


class FastSetMultiset:
    __slots__ = ("lo", "hi", "u", "seg", "cnt", "n", "mn", "mx", "mm", "med", "lowV", "lowB", "lowC", "highV", "highB", "highC", "d")

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
        self.med = self.mm = False  # min / max, medians, mex: tracked from their first query on (until then updates skip them)
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

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max, medians, mex current once asked for
        self.n += c
        self._insert(x, c)
        n = self.n
        if c > 0:
            if n == c:  # the set was empty
                if self.mm:
                    self.mn = self.mx = x
                if self.med:
                    self.lowV = self.highV = x
                    self.lowB = self.highB = 0
                    self.lowC = self.highC = c
                return
            if self.mm:
                if x < self.mn:
                    self.mn = x
                if x > self.mx:
                    self.mx = x
        else:
            if not n:
                return
            if self.mm:
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

    def _startMinMax(self):  # the first min() / max() (n > 0): from now on _add keeps both current
        self.mm = True
        self.mn, self.mx = self._kth(1), self._kth(self.n)

    def _startMedians(self):  # the first median query (n > 0): from now on _add keeps both medians current
        self.med = True
        n = self.n
        self.lowV, self.lowB, self.lowC = self._kthInfo((n + 1) >> 1)
        self.highV, self.highB, self.highC = self._kthInfo((n >> 1) + 1)

    def _resetCached(self):  # nothing counted, nothing tracked: as newly built
        self.med = self.mm = False
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

    # O(1 amortized) -- largest value; None if empty
    def max(self):
        if not self.n:
            return None
        if not self.mm:
            self._startMinMax()
        return self.mx

    # O(1 amortized) -- smallest value; None if empty
    def min(self):
        if not self.n:
            return None
        if not self.mm:
            self._startMinMax()
        return self.mn

    # O(log64(U)) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self.mx if self.mm else self._kth(self.n)
        self._add(v, -1)
        return v

    # O(log64(U)) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self.mn if self.mm else self._kth(1)
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
