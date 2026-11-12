# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/fenwick-with-xor-minmax-medians-mode/template.py
# @operations: add addCount clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow min mode pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
# @data-structure-type: fenwick
# @values: offline
# @keys: numbers
# @tracks: minmax medians mode
# @complexities:
#   add: log(N)
#   addCount: log(N)
#   clear: 1 amortized
#   count: log(N)
#   countDistinct: 1
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
#   medianHigh: 1
#   medianLow: 1
#   min: 1
#   mode: 1
#   pop: log(N)
#   popMax: log(N)
#   popMin: log(N)
#   remove: log(N)
#   removeAll: log(N)
#   removeCount: log(N)
#   removeInValRange: log(N) amortized
#   size: 1
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   xorOfAll: 1
#   xorOfGtX: log(N)
#   xorOfGteX: log(N)
#   xorOfInValRange: log(N)
#   xorOfKthLargestRange: log(N)
#   xorOfKthSmallestRange: log(N)
#   xorOfLargestK: log(N)
#   xorOfLtX: log(N)
#   xorOfLteX: log(N)
#   xorOfSmallestK: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: cnt[1*N] fc[1*N] fx[1*N]
#   tags: none
#   other: vals[1*N]
#   note: N = how many distinct values were given to the constructor; the arrays are allocated once. C++ integers also keep a hash table of at most 8*N ints from value to position
from random import getrandbits
from bisect import bisect_left, bisect_right


# Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
# to the constructor, one counting copies, one xor-ing the values with an odd count.
# k-th / sum of the k smallest walk down by binary lifting. The constructor only learns which values can appear (it
# compresses them); the multiset starts EMPTY. Every value you add must be one of them; query arguments (x, lo, hi)
# can be anything.


class FenwickMultiset:
    __slots__ = ("vals", "m", "top", "steps", "cnt", "fc", "fx", "n", "mn", "mx", "lowV", "lowB", "lowC", "highV",
        "highB", "highC", "bk", "bkAt", "fh", "fhAt", "xtotal", "salt", "d")

    # O(N log N) -- allValuesThatWillEverBeInsertedForOfflineCompression: every value you will EVER add (any order,
    # duplicates fine), only to compress values; this does NOT add them, the multiset starts empty; N = distinct values
    def __init__(self, allValuesThatWillEverBeInsertedForOfflineCompression):
        vals = self.vals = sorted(set(allValuesThatWillEverBeInsertedForOfflineCompression))
        m = self.m = len(vals)
        self.top = 1 << (m.bit_length() - 1) if m else 0  # highest power of two <= m, for binary lifting
        self.steps = tuple(1 << b for b in range(m.bit_length() - 1, -1, -1))  # top, top / 2, ..., 1
        self.cnt = [0] * m  # copies of vals[i]
        self.fc = [0] * (m + 1)  # Fenwick: copies
        self.fx = [0] * (m + 1)  # Fenwick: xor of the values with an odd count
        self.salt = getrandbits(60)  # hash containers key on salted values, so no fixed input can force collisions
        self.xtotal = 0  # xor of all values (copies count)
        self.bk, self.bkAt = {}, {}  # mode: count -> list of the values with that many copies; value -> its index there
        self.fh, self.fhAt = [], {}  # mode: max-heap of the counts that have a bucket; count -> its index in it
        self.n = self.d = 0

    def _fen(self, f, i, v):
        m = self.m
        i += 1
        while i <= m:
            f[i] += v
            i += i & -i

    def _pre(self, f, i):  # f's total over positions 0..i-1
        s = 0
        while i > 0:
            s += f[i]
            i &= i - 1
        return s

    def _insert(self, x, c, i=None):  # i: x's position in vals, if known
        if i is None:
            i = bisect_left(self.vals, x)  # x must be one of the given values
        cnt = self.cnt
        old = cnt[i]
        cnt[i] = old + c
        fc, m, j = self.fc, self.m, i + 1
        while j <= m:
            fc[j] += c
            j += j & -j
        if c & 1:  # x's parity flips
            fx, j = self.fx, i + 1
            while j <= self.m:
                fx[j] ^= x
                j += j & -j
        if not old:
            self.d += 1
        elif not old + c:
            self.d -= 1
        return old + c  # (x's new count)

    def _lt(self, x):
        fc, i, c = self.fc, bisect_left(self.vals, x), 0
        while i:
            c += fc[i]
            i &= i - 1
        return c

    def _le(self, x):
        fc, i, c = self.fc, bisect_right(self.vals, x), 0
        while i:
            c += fc[i]
            i &= i - 1
        return c

    def _countOf(self, x):
        i = bisect_left(self.vals, x)
        return self.cnt[i] if i < self.m and self.vals[i] == x else 0

    def _kth(self, k):  # binary lifting: the largest prefix with fewer than k copies ends right before the answer
        fc, m, pos = self.fc, self.m, 0
        for step in self.steps:
            nxt = pos + step
            if nxt <= m and fc[nxt] < k:
                pos = nxt
                k -= fc[nxt]
        return self.vals[pos]

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies)
        fc, m = self.fc, self.m
        pos, before = 0, 0
        for step in self.steps:
            nxt = pos + step
            if nxt <= m and before + fc[nxt] < k:
                pos = nxt
                before += fc[nxt]
        return self.vals[pos], before, self.cnt[pos]


    def _add(self, x, c, i=None):  # c copies of x (c < 0 removes); keeps min / max, both medians current
        self.n += c
        if c & 1:  # an odd number of copies flips x in or out of the xor of everything
            self.xtotal ^= x
        f = self._insert(x, c, i)  # x's new count
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
        n = self.n
        if c > 0:
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

    def _resetCached(self):  # nothing counted: as newly built
        self.bk, self.bkAt, self.fh, self.fhAt = {}, {}, [], {}
        self.n = self.d = 0
        self.xtotal = 0

    def _clearData(self):  # few distinct values present: zero only their slots and Fenwick paths, else wipe in bulk
        m, fc, cnt = self.m, self.fc, self.cnt
        if self.d * (self.top.bit_length() + 1) * 8 < m:
            fx = self.fx
            slots, k = [], 1
            while k <= self.n:  # the slot of the k-th smallest, by binary lifting; then skip its copies
                pos, step, before = 0, self.top, 0
                while step:
                    nxt = pos + step
                    if nxt <= m and before + fc[nxt] < k:
                        pos, before = nxt, before + fc[nxt]
                    step >>= 1
                slots.append(pos)
                k = before + cnt[pos] + 1
            for i in slots:
                cnt[i] = 0
                j = i + 1
                while j <= m:
                    fc[j] = 0
                    fx[j] = 0
                    j += j & -j
        else:
            self.cnt = [0] * m
            self.fc = [0] * (m + 1)
            self.fx = [0] * (m + 1)

    def _xpre(self, i):  # xor over positions 0..i-1
        f, res = self.fx, 0
        while i > 0:
            res ^= f[i]
            i &= i - 1
        return res

    def _xlt(self, x):
        return self._xpre(bisect_left(self.vals, x))

    def _xle(self, x):
        return self._xpre(bisect_right(self.vals, x))

    def _xorFirst(self, k):  # xor of the k smallest values (copies count): binary lifting, as for the k-th
        if k <= 0:
            return 0
        fc, fx, m = self.fc, self.fx, self.m
        pos, step, before, res = 0, self.top, 0, 0
        while step:
            nxt = pos + step
            if nxt <= m and before + fc[nxt] < k:
                pos = nxt
                before += fc[nxt]
                res ^= fx[nxt]
            step >>= 1
        return res ^ self.vals[pos] if (k - before) & 1 else res  # k - before copies of the answer's value

    # O(logN) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logN) -- add cnt copies of val (nothing if cnt <= 0)
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

    # O(logN) -- how many values > x (0 if there are none, e.g. on an empty set)
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(logN) -- how many values >= x (0 if there are none, e.g. on an empty set)
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(logN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logN) -- how many values < x (0 if there are none, e.g. on an empty set)
    def countLtX(self, x):
        return self._lt(x)

    # O(logN) -- how many values <= x (0 if there are none, e.g. on an empty set)
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

    # O(1) -- smallest value; raises IndexError if empty
    def min(self):
        if not self.n:
            raise IndexError("min: the set is empty")
        return self.mn

    # O(1) -- (a most frequent value, its count); raises IndexError if empty. C++ returns the smallest of the most
    # frequent values
    def mode(self):
        if not self.n:
            raise IndexError("mode: the set is empty")
        f = self.fh[0]
        v = self.bk[f ^ self.salt][0]
        return (v ^ self.salt if v.__class__ is int else v), f

    # O(logN) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (= popMin()),
    # pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logN) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self.mx
        self._add(v, -1)
        return v

    # O(logN) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self.mn
        self._add(v, -1)
        return v

    # O(logN) -- remove one copy of x if present; returns how many were removed (0 or 1: 0 if x isn't there, e.g. on an
    # empty set)
    def remove(self, x):
        i = bisect_left(self.vals, x)  # one lookup for both the check and the removal
        if i == self.m or self.vals[i] != x or not self.cnt[i]:
            return 0
        self._add(x, -1, i)
        return 1

    # O(logN) -- remove every copy of val; returns how many were removed (0 if val isn't there, e.g. on an empty set)
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logN) -- remove min(cnt, count(val)) copies of val; returns how many were removed (0 if val isn't there, e.g. on
    # an empty set)
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(logN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    # O(logN) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logN) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None

    # O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    def xorOfAll(self):
        return self.xtotal

    # O(logN) -- xor of the values > x (copies count; 0 if there are none)
    def xorOfGtX(self, x):
        return self.xtotal ^ self._xle(x)

    # O(logN) -- xor of the values >= x (copies count; 0 if there are none)
    def xorOfGteX(self, x):
        return self.xtotal ^ self._xlt(x)

    # O(logN) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    def xorOfInValRange(self, lo, hi):
        return self._xle(hi) ^ self._xlt(lo) if lo <= hi else 0

    # O(logN) -- xor of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    # largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises IndexError unless
    # 1 <= kFrom <= kTo <= size
    def xorOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._xorFirst(self.n - kFrom + 1) ^ self._xorFirst(self.n - kTo)

    # O(logN) -- xor of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    # smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError unless 1
    # <= kFrom <= kTo <= size
    def xorOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._xorFirst(kTo) ^ self._xorFirst(kFrom - 1)

    # O(logN) -- xor of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    # the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); raises IndexError unless 0 <=
    # k <= size
    def xorOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.xtotal ^ self._xorFirst(self.n - k)

    # O(logN) -- xor of the values < x (copies count; 0 if there are none)
    def xorOfLtX(self, x):
        return self._xlt(x)

    # O(logN) -- xor of the values <= x (copies count; 0 if there are none)
    def xorOfLteX(self, x):
        return self._xle(x)

    # O(logN) -- xor of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    # the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); raises IndexError unless 0
    # <= k <= size
    def xorOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._xorFirst(k)
