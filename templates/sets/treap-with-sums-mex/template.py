# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/treap-with-sums-mex/template.py
# @operations: add addCount count countDistinct countGtX countGteX countInValRange countLtX countLteX kthLargest kthSmallest largestLtX largestLteX max medianHigh medianLow mex min popMax popMin remove removeAll removeCount size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: treap
# @values: online
# @complexities:
#   add: log(N) expected
#   addCount: log(N) expected
#   count: log(N) expected
#   countDistinct: 1
#   countGtX: log(N) expected
#   countGteX: log(N) expected
#   countInValRange: log(N) expected
#   countLtX: log(N) expected
#   countLteX: log(N) expected
#   kthLargest: log(N) expected
#   kthSmallest: log(N) expected
#   largestLtX: log(N) expected
#   largestLteX: log(N) expected
#   max: 1
#   medianHigh: 1 amortized
#   medianLow: 1 amortized
#   mex: 1 amortized
#   min: 1
#   popMax: log(N) expected
#   popMin: log(N) expected
#   remove: log(N) expected
#   removeAll: log(N) expected
#   removeCount: log(N) expected
#   size: 1
#   smallestGtX: log(N) expected
#   smallestGteX: log(N) expected
#   sumAbsDiffToMedian: 1 amortized
#   sumAbsDiffToX: log(N) expected
#   sumAll: 1
#   sumGtX: log(N) expected
#   sumGteX: log(N) expected
#   sumInValRange: log(N) expected
#   sumKthLargestRange: log(N) expected
#   sumKthSmallestRange: log(N) expected
#   sumLargestK: log(N) expected
#   sumLtX: log(N) expected
#   sumLteX: log(N) expected
#   sumSmallestK: log(N) expected
#   build: 1
# @memory:
#   layout: none
#   node: key[1*N] cnt[1*N] size[1*N] dn[1*N] sum[1*N]
#   tags: none
#   other: children[2*N] prio[1*N]
#   note: N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, call resetPool() between test cases; Python: parallel lists per tree
from random import random


# Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
# its value, its copies, and the copies, sum and distinct values in its subtree. Nodes live in parallel lists (a node
# pool; node 0 is the empty tree) and removed nodes are reused. Updates split around x and merge back.


class TreapMultiset:
    __slots__ = ("K", "C", "Z", "S", "D", "P", "L", "R", "free", "root", "n", "mn", "mx", "med", "lowV", "lowB", "lowC", "lowS", "highV", "highB", "highC", "mexV", "total", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z, self.S = [0], [0], [0], [0]  # key, copies, copies below, sum below
        self.D = [0]  # distinct values below
        self.P, self.L, self.R = [0.0], [0], [0]  # priority, children
        self.free = []  # removed nodes, reused first
        self.med, self.mexV = False, -1  # medians / mex are tracked from their first query on; min / max always (set by the first add)
        self.root = self.n = self.total = self.d = 0

    def _new(self, x):
        if self.free:
            t = self.free.pop()
            self.K[t], self.C[t], self.P[t], self.L[t], self.R[t] = x, 0, random(), 0, 0
            return t
        self.K.append(x)
        self.C.append(0)
        self.Z.append(0)
        self.S.append(0)
        self.D.append(0)
        self.P.append(random())
        self.L.append(0)
        self.R.append(0)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
        self.S[t] = self.S[l] + self.S[r] + self.C[t] * self.K[t]
        self.D[t] = self.D[l] + self.D[r] + 1

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

    def _insert(self, x, c):
        a, b = self._split(self.root, x)
        m, b = self._split(b, x + 1)  # m: the node of x, or 0
        if not m:
            m = self._new(x)
            self.d += 1
        self.C[m] += c
        if self.C[m]:
            self._pull(m)
        else:
            self.free.append(m)
            m = 0
            self.d -= 1
        self.root = self._merge(self._merge(a, m), b)

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

    def _le(self, x):
        return self._lt(x + 1)

    def _countOf(self, x):
        K, L, R = self.K, self.L, self.R
        t = self.root
        while t and K[t] != x:
            t = L[t] if x < K[t] else R[t]
        return self.C[t]

    def _slt(self, x):  # sum of the values < x
        K, C, S, L, R = self.K, self.C, self.S, self.L, self.R
        t, res = self.root, 0
        while t:
            if K[t] < x:
                res += S[L[t]] + C[t] * K[t]
                t = R[t]
            else:
                t = L[t]
        return res

    def _sle(self, x):
        return self._slt(x + 1)

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

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies, sum before it)
        K, C, Z, S, L, R = self.K, self.C, self.Z, self.S, self.L, self.R
        t, before, acc = self.root, 0, 0
        while True:
            l = L[t]
            zl = before + Z[l]
            if k <= zl:
                t = l
            elif k <= zl + C[t]:
                return K[t], zl, C[t], acc + S[l]
            else:
                before = zl + C[t]
                acc += S[l] + C[t] * K[t]
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

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max (and medians / mex once asked for) current
        self.n += c
        self.total += c * x
        self._insert(x, c)
        n = self.n
        if c > 0:
            if x == self.mexV and x >= 0:  # x filled the mex (mexV is -1 until mex() is first called)
                self.mexV = self._findMex()
            if n == c:  # the set was empty
                self.mn = self.mx = x
                if self.med:
                    self.lowV = self.highV = x
                    self.lowB = self.highB = self.lowS = 0
                    self.lowC = self.highC = c
                return
            if x < self.mn:
                self.mn = x
            if x > self.mx:
                self.mx = x
        else:
            if 0 <= x < self.mexV and not self._countOf(x):  # the last copy of a value below the mex
                self.mexV = x
            if not n:
                return
            if x == self.mn:
                self.mn = self._kth(1)
            if x == self.mx:
                self.mx = self._kth(n)
        if not self.med:
            return
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

    def _startMedians(self):  # the first median query (n > 0): from now on _add keeps both medians current
        self.med = True
        n = self.n
        self.lowV, self.lowB, self.lowC, self.lowS = self._kthInfo((n + 1) >> 1)
        self.highV, self.highB, self.highC = self._kthInfo((n >> 1) + 1)[:3]

    def _sumFirst(self, k):  # sum of the k smallest values
        if k <= 0:
            return 0
        v, b, _, s = self._kthInfo(k)
        return s + (k - b) * v

    # O(logN expected) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logN expected) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(logN expected) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

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

    # O(logN expected) -- k-th largest value (1-indexed); raises IndexError unless 1 <= k <= size
    def kthLargest(self, k):
        if not 1 <= k <= self.n:
            raise IndexError(f"kthLargest: needs 1 <= k <= size, got k = {k}, size = {self.n}")
        return self._kth(self.n - k + 1)

    # O(logN expected) -- k-th smallest value (1-indexed); raises IndexError unless 1 <= k <= size
    def kthSmallest(self, k):
        if not 1 <= k <= self.n:
            raise IndexError(f"kthSmallest: needs 1 <= k <= size, got k = {k}, size = {self.n}")
        return self._kth(k)

    # O(logN expected) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(logN expected) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        c = self._le(x)
        return self._kth(c) if c else None

    # O(1) -- largest value; None if empty
    def max(self):
        return self.mx if self.n else None

    # O(1 amortized) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        if not self.n:
            return None
        if not self.med:
            self._startMedians()
        return self.highV

    # O(1 amortized) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        if not self.n:
            return None
        if not self.med:
            self._startMedians()
        return self.lowV

    # O(1 amortized) -- smallest non-negative integer not in the set
    def mex(self):
        if self.mexV < 0:  # the first call: from now on _add keeps it current
            self.mexV = self._findMex()
        return self.mexV

    # O(1) -- smallest value; None if empty
    def min(self):
        return self.mn if self.n else None

    # O(logN expected) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self.mx
        self._add(v, -1)
        return v

    # O(logN expected) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self.mn
        self._add(v, -1)
        return v

    # O(logN expected) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self.count(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logN expected) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logN expected) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(1) -- how many values (copies count)
    def size(self):
        return self.n

    # O(logN expected) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logN expected) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None

    # O(1 amortized) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    def sumAbsDiffToMedian(self):
        if not self.n:
            return 0
        if not self.med:
            self._startMedians()
        v, b, c, s = self.lowV, self.lowB, self.lowC, self.lowS
        return v * b - s + (self.total - s - c * v) - v * (self.n - b - c)

    # O(logN expected) -- sum of |v - x| over all values
    def sumAbsDiffToX(self, x):
        c, s = self._lt(x), self._slt(x)
        return x * c - s + (self.total - s) - x * (self.n - c)

    # O(1) -- sum of all values
    def sumAll(self):
        return self.total

    # O(logN expected) -- sum of the values > x
    def sumGtX(self, x):
        return self.total - self._sle(x)

    # O(logN expected) -- sum of the values >= x
    def sumGteX(self, x):
        return self.total - self._slt(x)

    # O(logN expected) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    def sumInValRange(self, lo, hi):
        return self._sle(hi) - self._slt(lo) if lo <= hi else 0

    # O(logN expected) -- sum of the i-th..j-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); raises IndexError unless 1 <= i <= j <= size
    def sumKthLargestRange(self, i, j):
        if not 1 <= i <= j <= self.n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= i <= j <= size, got i = {i}, j = {j}, size = {self.n}")
        return self._sumFirst(self.n - i + 1) - self._sumFirst(self.n - j)

    # O(logN expected) -- sum of the i-th..j-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= i <= j <= size
    def sumKthSmallestRange(self, i, j):
        if not 1 <= i <= j <= self.n:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= i <= j <= size, got i = {i}, j = {j}, size = {self.n}")
        return self._sumFirst(j) - self._sumFirst(i - 1)

    # O(logN expected) -- sum of the k largest values; raises IndexError unless 0 <= k <= size
    def sumLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.total - self._sumFirst(self.n - k)

    # O(logN expected) -- sum of the values < x
    def sumLtX(self, x):
        return self._slt(x)

    # O(logN expected) -- sum of the values <= x
    def sumLteX(self, x):
        return self._sle(x)

    # O(logN expected) -- sum of the k smallest values; raises IndexError unless 0 <= k <= size
    def sumSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._sumFirst(k)
