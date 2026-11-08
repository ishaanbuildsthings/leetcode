# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/value-tree-with-mex-medians-mode-gaps/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff mode pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
# @data-structure-type: value-tree
# @values: online-range
# @keys: numbers
# @tracks: medians mode gaps
# @complexities:
#   add: log(U) amortized
#   addCount: log(U) amortized
#   clear: 1 amortized
#   count: log(U)
#   countDistinct: 1
#   countDistinctInValRange: log(U)
#   countGtX: log(U)
#   countGteX: log(U)
#   countInValRange: log(U)
#   countLtX: log(U)
#   countLteX: log(U)
#   firstIndex: log(U)
#   kth: log(U)
#   largestLtX: log(U)
#   largestLteX: log(U)
#   lastIndex: log(U)
#   max: log(U)
#   maxGap: 1 amortized
#   medianHigh: 1
#   medianLow: 1
#   mex: log(U)
#   min: log(U)
#   minAdjacentDiff: 1 amortized
#   mode: 1
#   pop: log(U) amortized
#   popMax: log(U) amortized
#   popMin: log(U) amortized
#   remove: log(U) amortized
#   removeAll: log(U) amortized
#   removeCount: log(U) amortized
#   removeInValRange: log(U) amortized
#   size: 1
#   smallestGtX: log(U)
#   smallestGteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: c[1*log(U)] p[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per add of a new value, one node per level of its root path; U = hi - lo + 1. C++: each multiset owns its node pool (node 0 = empty); Python: dicts keyed by heap index
from random import getrandbits
from heapq import heappop, heappush

# Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
# each node keeping how many copies and how many distinct values (for mex) are below it. Sparse: dicts keyed by heap
# index over a power-of-two cover of [lo, hi]; a missing key is an empty block. k-th / sums of the k smallest descend
# by counts; mex descends to the first value >= 0 whose block isn't full.


class ValueTreeMultiset:
    __slots__ = ("lo", "hi", "B", "L", "R", "c", "p", "n", "lowV", "lowB", "lowC", "highV", "highB", "highC", "bk", "bkAt", "fh", "fhAt", "gc", "gmin", "gmax", "dups", "salt", "d")

    # O(1) -- an empty multiset for values in [lo, hi] (any integers, negative is fine)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.B = (hi - lo).bit_length()  # levels below the root: a value's path is the bits of v - lo, highest first
        self._clearData()
        self.salt = getrandbits(60)  # hash containers key on salted values, so no fixed input can force collisions
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.bk, self.bkAt = {}, {}  # mode: count -> list of the values with that many copies; value -> its index there
        self.fh, self.fhAt = [], {}  # mode: max-heap of the counts that have a bucket; count -> its index in it
        self.n = self.d = 0

    def _newNode(self):
        self.L.append(0)
        self.R.append(0)
        self.c.append(0)
        self.p.append(0)
        return len(self.L) - 1

    def _insert(self, x, c):
        L, R, cc = self.L, self.R, self.c
        off, t, path = x - self.lo, 1, [1]
        for h in range(self.B - 1, -1, -1):
            kids = R if off >> h & 1 else L
            nxt = kids[t]
            if not nxt:
                nxt = kids[t] = self._newNode()
            t = nxt
            path.append(t)
        old = cc[t]
        pres = (old + c > 0) - (old > 0)
        self.d += pres
        for i in path:
            cc[i] += c
        if pres:
            pp = self.p
            for i in path:
                pp[i] += pres
        return old + c  # (x's new count)

    def _prefix(self, f, x):  # f's total over the values < x
        if x <= self.lo:
            return 0
        if x > self.hi:
            return f[1]
        L, R, off, t, res = self.L, self.R, x - self.lo, 1, 0
        for h in range(self.B - 1, -1, -1):
            if off >> h & 1:
                res += f[L[t]]
                t = R[t]
            else:
                t = L[t]
            if not t:
                break
        return res

    def _lt(self, x):
        return self._prefix(self.c, x)

    def _le(self, x):
        return self._prefix(self.c, x + 1)

    def _countOf(self, x):  # the leaf of x
        if not self.lo <= x <= self.hi:
            return 0
        L, R, off, t = self.L, self.R, x - self.lo, 1
        for h in range(self.B - 1, -1, -1):
            t = R[t] if off >> h & 1 else L[t]
            if not t:
                return 0
        return self.c[t]

    def _kth(self, k):
        L, R, c, t, v = self.L, self.R, self.c, 1, 0
        for h in range(self.B - 1, -1, -1):
            l = L[t]
            cl = c[l]
            if k > cl:
                k -= cl
                t = R[t]
                v |= 1 << h
            else:
                t = l
        return v + self.lo

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies)
        L, R, c, t, v, before = self.L, self.R, self.c, 1, 0, 0
        for h in range(self.B - 1, -1, -1):
            l = L[t]
            cl = c[l]
            if before + cl < k:
                before += cl
                t = R[t]
                v |= 1 << h
            else:
                t = l
        return v + self.lo, before, c[t]

    # smallest non-negative integer not in the set (hi + 1 if all of [0, hi] are present)
    def _findMex(self):
        if self.lo > 0:
            return 0
        if self.hi < 0:
            return self.hi + 1
        L, R, p, off, t = self.L, self.R, self.p, -self.lo, 1
        later = []  # blocks right of the path to 0, nearest last: (node, its first value, levels below it)
        for h in range(self.B - 1, -1, -1):
            if off >> h & 1:
                t = R[t]
            else:
                later.append((R[t], (off >> h | 1) << h, h))
                t = L[t]
            if not t:
                return 0
        if not p[t]:
            return 0
        while later:
            t, base, h = later.pop()
            if p[t] == 1 << h:
                continue
            while t and h:  # the first missing value is inside: descend, preferring the left child
                h -= 1
                l = L[t]
                if p[l] == 1 << h:
                    base += 1 << h
                    t = R[t]
                else:
                    t = l
            return min(base + self.lo, self.hi + 1)
        return self.hi + 1

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps both medians current
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
            if n == c:  # the set was empty
                self.lowV = self.highV = x
                self.lowB = self.highB = 0
                self.lowC = self.highC = c
                return
        else:
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

    def _clearData(self):  # just the empty node 0 and the root 1 (the old lists are freed in bulk)
        self.L = [0, 0]
        self.R = [0, 0]
        self.c = [0, 0]
        self.p = [0, 0]

    def _distinctLt(self, x):  # distinct values < x
        return self._prefix(self.p, x)

    # O(logU amortized) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logU amortized) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    # instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logU) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(logU) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    def countDistinctInValRange(self, lo, hi):
        if lo > hi:
            return 0
        return self._distinctLt(hi) - self._distinctLt(lo) + (1 if self._countOf(hi) else 0)

    # O(logU) -- how many values > x
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(logU) -- how many values >= x
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(logU) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logU) -- how many values < x
    def countLtX(self, x):
        return self._lt(x)

    # O(logU) -- how many values <= x
    def countLteX(self, x):
        return self._le(x)

    # O(logU) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in
    # the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(logU) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    # kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1)

    # O(logU) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(logU) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        c = self._le(x)
        return self._kth(c) if c else None

    # O(logU) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is
    # not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(logU) -- largest value; raises IndexError if empty
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

    # O(logU) -- smallest non-negative integer not in the set
    def mex(self):
        return self._findMex()

    # O(logU) -- smallest value; raises IndexError if empty
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

    # O(logU amortized) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (=
    # popMin()), pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logU amortized) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(logU amortized) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self._kth(1)
        self._add(v, -1)
        return v

    # O(logU amortized) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logU amortized) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logU amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(logU amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    # O(logU) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logU) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None
