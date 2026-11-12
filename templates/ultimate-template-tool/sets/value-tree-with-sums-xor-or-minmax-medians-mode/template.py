# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/value-tree-with-sums-xor-or-minmax-medians-mode/template.py
# @operations: add addCount clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow min mode orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
# @data-structure-type: value-tree
# @values: online-range
# @keys: numbers
# @tracks: minmax medians mode
# @complexities:
#   add: log(U)
#   addCount: log(U)
#   clear: 1 amortized
#   count: log(U)
#   countDistinct: 1
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
#   max: 1
#   medianHigh: 1
#   medianLow: 1
#   min: 1
#   mode: 1
#   orOfAll: 1
#   orOfGtX: log(U)
#   orOfGteX: log(U)
#   orOfInValRange: log(U)
#   orOfKthLargestRange: log(U)
#   orOfKthSmallestRange: log(U)
#   orOfLargestK: log(U)
#   orOfLtX: log(U)
#   orOfLteX: log(U)
#   orOfSmallestK: log(U)
#   pop: log(U)
#   popMax: log(U)
#   popMin: log(U)
#   remove: log(U)
#   removeAll: log(U)
#   removeCount: log(U)
#   removeInValRange: log(U) amortized
#   size: 1
#   smallestGtX: log(U)
#   smallestGteX: log(U)
#   sumAbsDiffToMedian: 1
#   sumAbsDiffToX: log(U)
#   sumAll: 1
#   sumGtX: log(U)
#   sumGteX: log(U)
#   sumInValRange: log(U)
#   sumKthLargestRange: log(U)
#   sumKthSmallestRange: log(U)
#   sumLargestK: log(U)
#   sumLtX: log(U)
#   sumLteX: log(U)
#   sumSmallestK: log(U)
#   xorOfAll: 1
#   xorOfGtX: log(U)
#   xorOfGteX: log(U)
#   xorOfInValRange: log(U)
#   xorOfKthLargestRange: log(U)
#   xorOfKthSmallestRange: log(U)
#   xorOfLargestK: log(U)
#   xorOfLtX: log(U)
#   xorOfLteX: log(U)
#   xorOfSmallestK: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: c[1*log(U)] s[1*log(U)] x[1*log(U)] o[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per add of a new value, one node per level of its root path; U = hi - lo + 1. C++: each multiset owns its node pool (node 0 = empty); Python: dicts keyed by heap index
from random import getrandbits

# Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
# each node keeping how many copies, their sum,, their xor, their OR are below it. Sparse: dicts keyed by heap
# index over a power-of-two cover of [lo, hi]; a missing key is an empty block. k-th / sums of the k smallest descend
# by counts.


class ValueTreeMultiset:
    __slots__ = ("lo", "hi", "B", "L", "R", "c", "s", "x", "o", "n", "mn", "mx", "lowV", "lowB", "lowC", "lowS",
        "highV", "highB", "highC", "bk", "bkAt", "fh", "fhAt", "xtotal", "salt", "total", "d")

    # O(1) -- an empty multiset for values in [lo, hi] (any integers, negative is fine)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.B = (hi - lo).bit_length()  # levels below the root: a value's path is the bits of v - lo, highest first
        self._clearData()
        self.salt = getrandbits(60)  # hash containers key on salted values, so no fixed input can force collisions
        self.xtotal = 0  # xor of all values (copies count)
        self.bk, self.bkAt = {}, {}  # mode: count -> list of the values with that many copies; value -> its index there
        self.fh, self.fhAt = [], {}  # mode: max-heap of the counts that have a bucket; count -> its index in it
        self.n = self.total = self.d = 0

    def _newNode(self):
        self.L.append(0)
        self.R.append(0)
        self.c.append(0)
        self.s.append(0)
        self.x.append(0)
        self.o.append(0)
        return len(self.L) - 1

    def _insert(self, x, c):
        L, R, cc, ss = self.L, self.R, self.c, self.s
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
        cx = c * x
        for i in path:
            cc[i] += c
            ss[i] += cx
        if c & 1:  # x's parity flips
            xx = self.x
            for i in path:
                xx[i] ^= x
        if pres:  # x appeared or disappeared: the OR / AND up its path, each node from its two children
            oo = self.o
            oo[t] = x if old + c > 0 else 0
            for i in reversed(path[:-1]):
                oo[i] = oo[L[i]] | oo[R[i]]
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

    def _slt(self, x):
        return self._prefix(self.s, x)

    def _sle(self, x):
        return self._prefix(self.s, x + 1)

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

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies, sum before it)
        L, R, c, s, t, v, before, acc = self.L, self.R, self.c, self.s, 1, 0, 0, 0
        for h in range(self.B - 1, -1, -1):
            l = L[t]
            cl = c[l]
            if before + cl < k:
                before += cl
                acc += s[l]
                t = R[t]
                v |= 1 << h
            else:
                t = l
        return v + self.lo, before, c[t], acc


    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max, both medians current
        self.n += c
        self.total += c * x
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
        n = self.n
        if c > 0:
            if n == c:  # the set was empty
                self.mn = self.mx = x
                self.lowV = self.highV = x
                self.lowB = self.highB = self.lowS = 0
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
        # each median is a tracked rank: shift its (value, copies before, copies, sum before), and search again only
        # when the rank leaves the tracked value
        if x < self.lowV:
            self.lowB += c
            self.lowS += c * x
        elif x == self.lowV:
            self.lowC += c
        r = (n + 1) >> 1
        if not self.lowB < r <= self.lowB + self.lowC:
            self.lowV, self.lowB, self.lowC, self.lowS = self._kthInfo(r)
        if x < self.highV:
            self.highB += c
        elif x == self.highV:
            self.highC += c
        r = (n >> 1) + 1
        if not self.highB < r <= self.highB + self.highC:
            self.highV, self.highB, self.highC = self._kthInfo(r)[:3]

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

    def _sumFirst(self, k):  # sum of the k smallest values
        if k <= 0:
            return 0
        v, b, _, s = self._kthInfo(k)
        return s + (k - b) * v

    def _resetCached(self):  # nothing counted: as newly built
        self.bk, self.bkAt, self.fh, self.fhAt = {}, {}, [], {}
        self.n = self.d = 0
        self.total = 0
        self.xtotal = 0

    def _clearData(self):  # just the empty node 0 and the root 1 (the old lists are freed in bulk)
        self.L = [0, 0]
        self.R = [0, 0]
        self.c = [0, 0]
        self.s = [0, 0]
        self.x = [0, 0]
        self.o = [0, 0]

    def _xprefix(self, x):  # xor of the values < x (copies count)
        if x <= self.lo:
            return 0
        if x > self.hi:
            return self.xtotal
        L, R, f, off, t, res = self.L, self.R, self.x, x - self.lo, 1, 0
        for h in range(self.B - 1, -1, -1):
            if off >> h & 1:
                res ^= f[L[t]]
                t = R[t]
            else:
                t = L[t]
            if not t:
                break
        return res

    def _xlt(self, x):
        return self._xprefix(x)

    def _xle(self, x):
        return self._xprefix(x + 1)

    def _xorFirst(self, k):  # xor of the k smallest values (copies count)
        if k <= 0:
            return 0
        L, R, c, f, t, v, res = self.L, self.R, self.c, self.x, 1, 0, 0
        for h in range(self.B - 1, -1, -1):
            l = L[t]
            cl = c[l]
            if k > cl:
                k -= cl
                res ^= f[l]
                t = R[t]
                v |= 1 << h
            else:
                t = l
        return res ^ (v + self.lo) if k & 1 else res  # k copies of the leaf's value left

    def _orIn(self, lo, hi):  # OR of the values in [lo, hi]: the blocks that cover it, from the root down
        lo, hi = max(lo, self.lo) - self.lo, min(hi, self.hi) - self.lo
        if lo > hi:
            return 0
        L, R, f, res = self.L, self.R, self.o, 0
        stack = [(1, 0, self.B)]
        while stack:
            t, base, h = stack.pop()
            last = base + (1 << h) - 1
            if not t or last < lo or base > hi:
                continue
            if lo <= base and last <= hi:
                res |= f[t]
                continue
            h -= 1
            stack.append((L[t], base, h))
            stack.append((R[t], base + (1 << h), h))
        return res

    def _orLe(self, x):  # OR of the values <= x
        return self._orIn(self.lo, x)

    def _orGe(self, x):  # OR of the values >= x
        return self._orIn(x, self.hi)

    # O(logU) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logU) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1 amortized) -- remove everything (fine on an empty set): afterwards it is as if newly built (same constructor
    # arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logU) -- how many copies of x (0 if x isn't there, e.g. on an empty set)
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values (0 if empty)
    def countDistinct(self):
        return self.d

    # O(logU) -- how many values > x (0 if there are none, e.g. on an empty set)
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(logU) -- how many values >= x (0 if there are none, e.g. on an empty set)
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(logU) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logU) -- how many values < x (0 if there are none, e.g. on an empty set)
    def countLtX(self, x):
        return self._lt(x)

    # O(logU) -- how many values <= x (0 if there are none, e.g. on an empty set)
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

    # O(1) -- bitwise OR of all values; 0 if empty
    def orOfAll(self):
        return self.o[1]

    # O(logU) -- bitwise OR of the values > x; 0 if there are none
    def orOfGtX(self, x):
        return self._orGe(x + 1)

    # O(logU) -- bitwise OR of the values >= x; 0 if there are none
    def orOfGteX(self, x):
        return self._orGe(x)

    # O(logU) -- bitwise OR of the values v with lo <= v <= hi; 0 if there are none
    def orOfInValRange(self, lo, hi):
        return self._orIn(lo, hi) if lo <= hi else 0

    # O(logU) -- bitwise OR of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._orIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logU) -- bitwise OR of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError
    # unless 1 <= kFrom <= kTo <= size
    def orOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._orIn(self._kth(kFrom), self._kth(kTo))

    # O(logU) -- bitwise OR of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k =
    # 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); raises IndexError
    # unless 0 <= k <= size
    def orOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orGe(self._kth(self.n - k + 1)) if k else 0

    # O(logU) -- bitwise OR of the values < x; 0 if there are none
    def orOfLtX(self, x):
        return self._orLe(x - 1)

    # O(logU) -- bitwise OR of the values <= x; 0 if there are none
    def orOfLteX(self, x):
        return self._orLe(x)

    # O(logU) -- bitwise OR of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k =
    # 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); raises IndexError
    # unless 0 <= k <= size
    def orOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orLe(self._kth(k)) if k else 0

    # O(logU) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (= popMin()),
    # pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logU) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self.mx
        self._add(v, -1)
        return v

    # O(logU) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self.mn
        self._add(v, -1)
        return v

    # O(logU) -- remove one copy of x if present; returns how many were removed (0 or 1: 0 if x isn't there, e.g. on an
    # empty set)
    def remove(self, x):
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logU) -- remove every copy of val; returns how many were removed (0 if val isn't there, e.g. on an empty set)
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logU) -- remove min(cnt, count(val)) copies of val; returns how many were removed (0 if val isn't there, e.g. on
    # an empty set)
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

    # O(1) -- how many values (copies count; 0 if empty)
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

    # O(1) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    def sumAbsDiffToMedian(self):
        if not self.n:
            return 0
        v, b, c, s = self.lowV, self.lowB, self.lowC, self.lowS
        return v * b - s + (self.total - s - c * v) - v * (self.n - b - c)

    # O(logU) -- sum of |v - x| over all values (0 if empty)
    def sumAbsDiffToX(self, x):
        c, s = self._lt(x), self._slt(x)
        return x * c - s + (self.total - s) - x * (self.n - c)

    # O(1) -- sum of all values (0 if empty)
    def sumAll(self):
        return self.total

    # O(logU) -- sum of the values > x (0 if there are none, e.g. on an empty set)
    def sumGtX(self, x):
        return self.total - self._sle(x)

    # O(logU) -- sum of the values >= x (0 if there are none, e.g. on an empty set)
    def sumGteX(self, x):
        return self.total - self._slt(x)

    # O(logU) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    def sumInValRange(self, lo, hi):
        return self._sle(hi) - self._slt(lo) if lo <= hi else 0

    # O(logU) -- sum of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    # largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises IndexError unless
    # 1 <= kFrom <= kTo <= size
    def sumKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._sumFirst(self.n - kFrom + 1) - self._sumFirst(self.n - kTo)

    # O(logU) -- sum of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    # smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError unless 1
    # <= kFrom <= kTo <= size
    def sumKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._sumFirst(kTo) - self._sumFirst(kFrom - 1)

    # O(logU) -- sum of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    # the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); raises IndexError unless 0 <=
    # k <= size
    def sumLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.total - self._sumFirst(self.n - k)

    # O(logU) -- sum of the values < x (0 if there are none, e.g. on an empty set)
    def sumLtX(self, x):
        return self._slt(x)

    # O(logU) -- sum of the values <= x (0 if there are none, e.g. on an empty set)
    def sumLteX(self, x):
        return self._sle(x)

    # O(logU) -- sum of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    # the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); raises IndexError unless 0
    # <= k <= size
    def sumSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._sumFirst(k)

    # O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    def xorOfAll(self):
        return self.xtotal

    # O(logU) -- xor of the values > x (copies count; 0 if there are none)
    def xorOfGtX(self, x):
        return self.xtotal ^ self._xle(x)

    # O(logU) -- xor of the values >= x (copies count; 0 if there are none)
    def xorOfGteX(self, x):
        return self.xtotal ^ self._xlt(x)

    # O(logU) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    def xorOfInValRange(self, lo, hi):
        return self._xle(hi) ^ self._xlt(lo) if lo <= hi else 0

    # O(logU) -- xor of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    # largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises IndexError unless
    # 1 <= kFrom <= kTo <= size
    def xorOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._xorFirst(self.n - kFrom + 1) ^ self._xorFirst(self.n - kTo)

    # O(logU) -- xor of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is just the
    # smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError unless 1
    # <= kFrom <= kTo <= size
    def xorOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._xorFirst(kTo) ^ self._xorFirst(kFrom - 1)

    # O(logU) -- xor of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    # the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); raises IndexError unless 0 <=
    # k <= size
    def xorOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.xtotal ^ self._xorFirst(self.n - k)

    # O(logU) -- xor of the values < x (copies count; 0 if there are none)
    def xorOfLtX(self, x):
        return self._xlt(x)

    # O(logU) -- xor of the values <= x (copies count; 0 if there are none)
    def xorOfLteX(self, x):
        return self._xle(x)

    # O(logU) -- xor of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k = 1 just
    # the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); raises IndexError unless 0
    # <= k <= size
    def xorOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._xorFirst(k)
