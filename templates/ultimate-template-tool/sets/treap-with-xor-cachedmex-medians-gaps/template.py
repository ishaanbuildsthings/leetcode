# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/treap-with-xor-cachedmex-medians-gaps/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow mex min minAdjacentDiff pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
# @data-structure-type: treap
# @values: online
# @keys: numbers
# @tracks: medians mex gaps
# @complexities:
#   add: log(N) amortized expected
#   addCount: log(N) amortized expected
#   clear: 1 amortized
#   count: log(N) expected
#   countDistinct: 1
#   countDistinctInValRange: log(N) expected
#   countGtX: log(N) expected
#   countGteX: log(N) expected
#   countInValRange: log(N) expected
#   countLtX: log(N) expected
#   countLteX: log(N) expected
#   firstIndex: log(N) expected
#   kth: log(N) expected
#   largestLtX: log(N) expected
#   largestLteX: log(N) expected
#   lastIndex: log(N) expected
#   max: log(N) expected
#   maxGap: 1 amortized
#   medianHigh: 1
#   medianLow: 1
#   mex: 1
#   min: log(N) expected
#   minAdjacentDiff: 1 amortized
#   pop: log(N) amortized expected
#   popMax: log(N) amortized expected
#   popMin: log(N) amortized expected
#   remove: log(N) amortized expected
#   removeAll: log(N) amortized expected
#   removeCount: log(N) amortized expected
#   removeInValRange: log(N) amortized expected
#   size: 1
#   smallestGtX: log(N) expected
#   smallestGteX: log(N) expected
#   xorOfAll: 1
#   xorOfGtX: log(N) expected
#   xorOfGteX: log(N) expected
#   xorOfInValRange: log(N) expected
#   xorOfKthLargestRange: log(N) expected
#   xorOfKthSmallestRange: log(N) expected
#   xorOfLargestK: log(N) expected
#   xorOfLtX: log(N) expected
#   xorOfLteX: log(N) expected
#   xorOfSmallestK: log(N) expected
#   build: 1
# @memory:
#   layout: none
#   node: key[1*N] cnt[1*N] size[1*N] dn[1*N] xor[1*N]
#   tags: none
#   other: children[2*N] prio[1*N]
#   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree
from random import getrandbits
from heapq import heappop, heappush
from random import random


# Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
# its value, its copies, and the copies, xor and distinct values in its subtree. Nodes live in parallel lists (a node
# pool; node 0 is the empty tree) and removed nodes are reused. Updates split around x and merge back.


class TreapMultiset:
    __slots__ = ("K", "C", "Z", "X", "D", "P", "L", "R", "free", "root", "n", "lowV", "lowB", "lowC", "highV", "highB", "highC", "mexV", "gc", "gmin", "gmax", "dups", "xtotal", "salt", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z = [0], [0], [0]  # key, copies, copies below
        self.D = [0]  # distinct values below
        self.X = [0]  # xor of the values below with an odd count
        self.P, self.L, self.R = [0.0], [0], [0]  # priority, children
        self.free = []  # removed nodes, reused first
        self.salt = getrandbits(60)  # hash containers key on salted values, so no fixed input can force collisions
        self.xtotal = 0  # xor of all values (copies count)
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.mexV = 0  # the mex, kept current (0 for the empty set)
        self.root = self.n = self.d = 0

    def _new(self, x):
        if self.free:
            t = self.free.pop()
            self.K[t], self.C[t], self.P[t], self.L[t], self.R[t] = x, 0, random(), 0, 0
            return t
        self.K.append(x)
        self.C.append(0)
        self.Z.append(0)
        self.D.append(0)
        self.X.append(0)
        self.P.append(random())
        self.L.append(0)
        self.R.append(0)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
        self.D[t] = self.D[l] + self.D[r] + 1
        self.X[t] = self.X[l] ^ self.X[r] ^ (self.K[t] if self.C[t] & 1 else 0)

    def _split(self, t, x):  # (keys < x, keys >= x)
        if not t:
            return 0, 0
        if self.K[t] < x:
            a, b = self._split(self.R[t], x)
            self.R[t] = a
            self._pull(t)
            return t, b
        a, b = self._split(self.L[t], x)
        self.L[t] = b
        self._pull(t)
        return a, t

    def _splitLe(self, t, x):  # (keys <= x, keys > x)
        if not t:
            return 0, 0
        if x < self.K[t]:
            a, b = self._splitLe(self.L[t], x)
            self.L[t] = b
            self._pull(t)
            return a, t
        a, b = self._splitLe(self.R[t], x)
        self.R[t] = a
        self._pull(t)
        return t, b

    def _merge(self, a, b):  # every key in a < every key in b
        if not a or not b:
            return a or b
        if self.P[a] > self.P[b]:
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        self.L[b] = self._merge(a, self.L[b])
        self._pull(b)
        return b

    def _insert(self, x, c):  # walks once: a value already present never needs a split or merge
        K, L, R, C = self.K, self.L, self.R, self.C
        path, t = [], self.root
        while t:
            path.append(t)
            key = K[t]
            if x < key:
                t = L[t]
            elif key < x:
                t = R[t]
            else:
                break
        if t:
            f = C[t] = C[t] + c
            path.pop()
            if f:
                self._pull(t)
                cur = t
            else:
                self.free.append(t)
                self.d -= 1
                cur = self._merge(L[t], R[t])
        else:
            m = self._new(x)
            self.d += 1
            f = C[m] = c
            P, prio, i = self.P, self.P[m], 0
            while i < len(path) and P[path[i]] >= prio:  # the new node goes where its priority belongs
                i += 1
            if i < len(path):
                L[m], R[m] = self._split(path[i], x)
                del path[i:]
            self._pull(m)
            cur = m
        while path:
            q = path.pop()
            if x < K[q]:
                L[q] = cur
            else:
                R[q] = cur
            l, r = self.L[q], self.R[q]
            self.Z[q] = self.Z[l] + self.Z[r] + self.C[q]
            self.D[q] = self.D[l] + self.D[r] + 1
            self.X[q] = self.X[l] ^ self.X[r] ^ (self.K[q] if self.C[q] & 1 else 0)
            cur = q
        self.root = cur
        return f  # (x's new count)

    def _lt(self, x):  # copies of values < x
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t, res = self.root, 0
        while t:
            if K[t] < x:
                res += Z[L[t]] + C[t]
                t = R[t]
            else:
                t = L[t]
        return res

    def _le(self, x):  # copies of values <= x
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t, res = self.root, 0
        while t:
            if x < K[t]:
                t = L[t]
            else:
                res += Z[L[t]] + C[t]
                t = R[t]
        return res

    def _countOf(self, x):
        K, L, R = self.K, self.L, self.R
        t = self.root
        while t and K[t] != x:
            t = L[t] if x < K[t] else R[t]
        return self.C[t]

    def _kth(self, k):
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t = self.root
        while True:
            zl = Z[L[t]]
            if k <= zl:
                t = L[t]
            elif k <= zl + C[t]:
                return K[t]
            else:
                k -= zl + C[t]
                t = R[t]

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies)
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t, before = self.root, 0
        while True:
            l = L[t]
            zl = before + Z[l]
            if k <= zl:
                t = l
            elif k <= zl + C[t]:
                return K[t], zl, C[t]
            else:
                before = zl + C[t]
                t = R[t]

    def _distinctLt(self, x):  # distinct values < x
        K, D, L, R = self.K, self.D, self.L, self.R
        t, res = self.root, 0
        while t:
            if K[t] < x:
                res += D[L[t]] + 1
                t = R[t]
            else:
                t = L[t]
        return res

    # smallest non-negative integer not in the set. With c0 distinct negatives, the distinct values >= 0
    # in order v_0 < v_1 < ... satisfy v_j >= j, and v_j == j means 0..v_j are all present; the answer is the first j
    # with v_j > j (or how many there are). One walk down: at a node of distinct rank c0 + j, go right if v_j == j.
    def _findMex(self):
        K, D, L, R = self.K, self.D, self.L, self.R
        c0 = self._distinctLt(0)
        t, before, res = self.root, -c0, self.d - c0  # before: distinct values >= 0 left of t's subtree
        while t:
            j = before + D[L[t]]
            if K[t] < 0 or K[t] == j:
                before = j + 1
                t = R[t]
            else:
                res = j
                t = L[t]
        return res

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps both medians, the mex current
        self.n += c
        if c & 1:  # an odd number of copies flips x in or out of the xor of everything
            self.xtotal ^= x
        f = self._insert(x, c)  # x's new count
        g = f - c  # x's old count
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
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0
        self.n = self.d = 0
        self.xtotal = 0

    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)
        self.K = [0]
        self.C = [0]
        self.Z = [0]
        self.D = [0]
        self.X = [0]
        self.L = [0]
        self.R = [0]
        self.P = [0.0]
        self.free = []
        self.root = 0

    def _xlt(self, x):  # xor of the values < x (copies count)
        K, C, X, L, R = self.K, self.C, self.X, self.L, self.R
        t, res = self.root, 0
        while t:
            if K[t] < x:
                res ^= X[L[t]] ^ (K[t] if C[t] & 1 else 0)
                t = R[t]
            else:
                t = L[t]
        return res

    def _xle(self, x):  # xor of the values <= x (copies count)
        K, C, X, L, R = self.K, self.C, self.X, self.L, self.R
        t, res = self.root, 0
        while t:
            if x < K[t]:
                t = L[t]
            else:
                res ^= X[L[t]] ^ (K[t] if C[t] & 1 else 0)
                t = R[t]
        return res

    def _xorFirst(self, k):  # xor of the k smallest values (copies count)
        if k <= 0:
            return 0
        K, C, Z, X, L, R = self.K, self.C, self.Z, self.X, self.L, self.R
        t, res = self.root, 0
        while True:
            l = L[t]
            zl = Z[l]
            if k <= zl:
                t = l
            elif k <= zl + C[t]:
                return res ^ X[l] ^ (K[t] if (k - zl) & 1 else 0)
            else:
                k -= zl + C[t]
                res ^= X[l] ^ (K[t] if C[t] & 1 else 0)
                t = R[t]

    # O(logN amortized expected) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logN amortized expected) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it
    # instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logN expected) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(logN expected) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    def countDistinctInValRange(self, lo, hi):
        if lo > hi:
            return 0
        return self._distinctLt(hi) - self._distinctLt(lo) + (1 if self._countOf(hi) else 0)

    # O(logN expected) -- how many values > x
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(logN expected) -- how many values >= x
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(logN expected) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logN expected) -- how many values < x
    def countLtX(self, x):
        return self._lt(x)

    # O(logN expected) -- how many values <= x
    def countLteX(self, x):
        return self._le(x)

    # O(logN expected) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is
    # not in the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(logN expected) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    # kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1)

    # O(logN expected) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(logN expected) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        c = self._le(x)
        return self._kth(c) if c else None

    # O(logN expected) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1
    # if x is not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(logN expected) -- largest value; raises IndexError if empty
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

    # O(1) -- smallest non-negative integer not in the set
    def mex(self):
        return self.mexV

    # O(logN expected) -- smallest value; raises IndexError if empty
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

    # O(logN amortized expected) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the
    # smallest (= popMin()), pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logN amortized expected) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(logN amortized expected) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self._kth(1)
        self._add(v, -1)
        return v

    # O(logN amortized expected) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logN amortized expected) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logN amortized expected) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(logN amortized expected) -- remove every value v with lo <= v <= hi; returns how many copies were removed
    # (0 if lo > hi)
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

    # O(logN expected) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logN expected) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None

    # O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    def xorOfAll(self):
        return self.xtotal

    # O(logN expected) -- xor of the values > x (copies count)
    def xorOfGtX(self, x):
        return self.xtotal ^ self._xle(x)

    # O(logN expected) -- xor of the values >= x (copies count)
    def xorOfGteX(self, x):
        return self.xtotal ^ self._xlt(x)

    # O(logN expected) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    def xorOfInValRange(self, lo, hi):
        return self._xle(hi) ^ self._xlt(lo) if lo <= hi else 0

    # O(logN expected) -- xor of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def xorOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._xorFirst(self.n - kFrom + 1) ^ self._xorFirst(self.n - kTo)

    # O(logN expected) -- xor of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive: (1, 1) is
    # just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises IndexError
    # unless 1 <= kFrom <= kTo <= size
    def xorOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._xorFirst(kTo) ^ self._xorFirst(kFrom - 1)

    # O(logN expected) -- xor of the k largest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k
    # = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5); raises IndexError
    # unless 0 <= k <= size
    def xorOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.xtotal ^ self._xorFirst(self.n - k)

    # O(logN expected) -- xor of the values < x (copies count)
    def xorOfLtX(self, x):
        return self._xlt(x)

    # O(logN expected) -- xor of the values <= x (copies count)
    def xorOfLteX(self, x):
        return self._xle(x)

    # O(logN expected) -- xor of the k smallest values; k is a COUNT, not an index: k = 0 takes no values (returns 0), k
    # = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2); raises IndexError
    # unless 0 <= k <= size
    def xorOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._xorFirst(k)
