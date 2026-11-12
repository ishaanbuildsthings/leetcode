# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/treap-with-gcd-lcm-minmax/template.py
# @operations: add addCount clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex gcdOfAll gcdOfGtX gcdOfGteX gcdOfInValRange gcdOfKthLargestRange gcdOfKthSmallestRange gcdOfLargestK gcdOfLtX gcdOfLteX gcdOfSmallestK kth largestLtX largestLteX lastIndex lcmOfAll lcmOfGtX lcmOfGteX lcmOfInValRange lcmOfKthLargestRange lcmOfKthSmallestRange lcmOfLargestK lcmOfLtX lcmOfLteX lcmOfSmallestK max medianHigh medianLow min pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
# @data-structure-type: treap
# @values: online
# @keys: numbers
# @tracks: minmax
# @complexities:
#   add: log(N)*log(U) expected
#   addCount: log(N)*log(U) expected
#   clear: 1 amortized
#   count: log(N) expected
#   countDistinct: 1
#   countGtX: log(N) expected
#   countGteX: log(N) expected
#   countInValRange: log(N) expected
#   countLtX: log(N) expected
#   countLteX: log(N) expected
#   firstIndex: log(N) expected
#   gcdOfAll: 1
#   gcdOfGtX: log(N)*log(U) expected
#   gcdOfGteX: log(N)*log(U) expected
#   gcdOfInValRange: log(N)*log(U) expected
#   gcdOfKthLargestRange: log(N)*log(U) expected
#   gcdOfKthSmallestRange: log(N)*log(U) expected
#   gcdOfLargestK: log(N)*log(U) expected
#   gcdOfLtX: log(N)*log(U) expected
#   gcdOfLteX: log(N)*log(U) expected
#   gcdOfSmallestK: log(N)*log(U) expected
#   kth: log(N) expected
#   largestLtX: log(N) expected
#   largestLteX: log(N) expected
#   lastIndex: log(N) expected
#   lcmOfAll: 1
#   lcmOfGtX: log(N)*log(U) expected
#   lcmOfGteX: log(N)*log(U) expected
#   lcmOfInValRange: log(N)*log(U) expected
#   lcmOfKthLargestRange: log(N)*log(U) expected
#   lcmOfKthSmallestRange: log(N)*log(U) expected
#   lcmOfLargestK: log(N)*log(U) expected
#   lcmOfLtX: log(N)*log(U) expected
#   lcmOfLteX: log(N)*log(U) expected
#   lcmOfSmallestK: log(N)*log(U) expected
#   max: 1
#   medianHigh: log(N) expected
#   medianLow: log(N) expected
#   min: 1
#   pop: log(N)*log(U) expected
#   popMax: log(N)*log(U) expected
#   popMin: log(N)*log(U) expected
#   remove: log(N)*log(U) expected
#   removeAll: log(N)*log(U) expected
#   removeCount: log(N)*log(U) expected
#   removeInValRange: log(N)*log(U) expected
#   size: 1
#   smallestGtX: log(N) expected
#   smallestGteX: log(N) expected
#   build: 1
# @memory:
#   layout: none
#   node: key[1*N] cnt[1*N] size[1*N] gcd[1*N] lcm[1*N]
#   tags: none
#   other: children[2*N] prio[1*N]
#   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree
# lcmOf... answers -1 once the LCM passes cap, so it never overflows: cap is a constructor argument, the largest
# value (2**63 - 1) by default; pass your own, e.g. TreapMultiset(cap=10**9). Removing values is safe: every node
# keeps the capped LCM of just its own values, so once the values that pushed it past cap are gone, lcmOf... is exact
# again. Values must be >= 0 (add / addCount of a negative one is an error). An empty selection gives the identity:
# gcd 0, LCM 1.
from math import gcd
from random import random


# Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
# its value, its copies, and totals over its subtree: copies, gcd, LCM. Nodes live in parallel lists (a node pool; node
# 0 is the empty tree) and removed nodes are reused. Updates split around x and merge back.


class TreapMultiset:
    __slots__ = ("K", "C", "Z", "G", "M", "P", "L", "R", "free", "root", "n", "mn", "mx", "d", "cap")

    # O(1) -- an empty multiset
    def __init__(self, cap=2**63 - 1):
        self.cap = cap
        self.K, self.C, self.Z = [0], [0], [0]  # key, copies, copies below
        self.G = [0]  # gcd of the values below
        self.M = [1]  # capped LCM of the values below (the empty tree's: 1)
        self.P, self.L, self.R = [0.0], [0], [0]  # priority, children
        self.free = []  # removed nodes, reused first
        self.root = self.n = self.d = 0

    def _new(self, x):
        if self.free:
            t = self.free.pop()
            self.K[t], self.C[t], self.P[t], self.L[t], self.R[t] = x, 0, random(), 0, 0
            return t
        self.K.append(x)
        self.C.append(0)
        self.Z.append(0)
        self.G.append(0)
        self.M.append(1)
        self.P.append(random())
        self.L.append(0)
        self.R.append(0)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
        self.G[t] = gcd(gcd(self.G[l], self.G[r]), self.K[t])
        self.M[t] = self._lc(self._lc(self.M[l], self.M[r]), self.K[t])

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
            self.G[q] = gcd(gcd(self.G[l], self.G[r]), self.K[q])
            self.M[q] = self._lc(self._lc(self.M[l], self.M[r]), self.K[q])
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


    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max current
        self.n += c
        f = self._insert(x, c)  # x's new count
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

    def _resetCached(self):  # nothing counted: as newly built
        self.n = self.d = 0

    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)
        self.K = [0]
        self.C = [0]
        self.Z = [0]
        self.G = [0]
        self.L = [0]
        self.R = [0]
        self.M = [1]
        self.P = [0.0]
        self.free = []
        self.root = 0

    def _gcdLe(self, x):  # gcd of the values <= x
        K, F, L, R = self.K, self.G, self.L, self.R
        t, res = self.root, 0
        while t:
            if x < K[t]:
                t = L[t]
            else:
                res = gcd(res, gcd(F[L[t]], K[t]))
                t = R[t]
        return res

    def _gcdGe(self, x):  # gcd of the values >= x
        K, F, L, R = self.K, self.G, self.L, self.R
        t, res = self.root, 0
        while t:
            if K[t] < x:
                t = R[t]
            else:
                res = gcd(res, gcd(F[R[t]], K[t]))
                t = L[t]
        return res

    def _gcdIn(self, lo, hi):  # gcd of the values in [lo, hi] (lo <= hi)
        K, F, L, R = self.K, self.G, self.L, self.R
        t = self.root
        while t and not lo <= K[t] <= hi:  # down to the highest node inside [lo, hi]
            t = L[t] if hi < K[t] else R[t]
        if not t:
            return 0
        res = gcd(0, K[t])
        u = L[t]  # its left side is <= hi: keep what is >= lo
        while u:
            if lo <= K[u]:
                res = gcd(res, gcd(K[u], F[R[u]]))
                u = L[u]
            else:
                u = R[u]
        u = R[t]  # its right side is >= lo: keep what is <= hi
        while u:
            if K[u] <= hi:
                res = gcd(res, gcd(K[u], F[L[u]]))
                u = R[u]
            else:
                u = L[u]
        return res

    def _lcmLe(self, x):  # capped LCM of the values <= x
        K, F, L, R = self.K, self.M, self.L, self.R
        t, res = self.root, 1
        while t:
            if x < K[t]:
                t = L[t]
            else:
                res = self._lc(res, self._lc(F[L[t]], K[t]))
                t = R[t]
        return res

    def _lcmGe(self, x):  # capped LCM of the values >= x
        K, F, L, R = self.K, self.M, self.L, self.R
        t, res = self.root, 1
        while t:
            if K[t] < x:
                t = R[t]
            else:
                res = self._lc(res, self._lc(F[R[t]], K[t]))
                t = L[t]
        return res

    def _lcmIn(self, lo, hi):  # capped LCM of the values in [lo, hi] (lo <= hi)
        K, F, L, R = self.K, self.M, self.L, self.R
        t = self.root
        while t and not lo <= K[t] <= hi:  # down to the highest node inside [lo, hi]
            t = L[t] if hi < K[t] else R[t]
        if not t:
            return 1
        res = self._lc(1, K[t])
        u = L[t]  # its left side is <= hi: keep what is >= lo
        while u:
            if lo <= K[u]:
                res = self._lc(res, self._lc(K[u], F[R[u]]))
                u = L[u]
            else:
                u = R[u]
        u = R[t]  # its right side is >= lo: keep what is <= hi
        while u:
            if K[u] <= hi:
                res = self._lc(res, self._lc(K[u], F[L[u]]))
                u = R[u]
            else:
                u = L[u]
        return res

    # O(logN * logU expected) -- add one copy of x; raises ValueError if x < 0
    def add(self, x):
        if x < 0:
            raise ValueError(f"TreapMultiset.add: {x} is negative (the LCM needs values >= 0)")
        self._add(x, 1)

    # O(logN * logU expected) -- add cnt copies of val (nothing if cnt <= 0); raises ValueError if val < 0
    def addCount(self, val, cnt):
        if val < 0:
            raise ValueError(f"TreapMultiset.addCount: {val} is negative (the LCM needs values >= 0)")
        if cnt > 0:
            self._add(val, cnt)

    # O(1) -- LCM (-1 once it passes cap) of all values; 1 if empty
    def lcmOfAll(self):
        return self.M[self.root]

    # O(logN * logU expected) -- LCM (-1 once it passes cap) of the values > x; 1 if there are none
    def lcmOfGtX(self, x):
        return self._lcmGe(x + 1)

    # O(logN * logU expected) -- LCM (-1 once it passes cap) of the values >= x; 1 if there are none
    def lcmOfGteX(self, x):
        return self._lcmGe(x)

    # O(logN * logU expected) -- LCM (-1 once it passes cap) of the values v with lo <= v <= hi; 1 if there are none
    def lcmOfInValRange(self, lo, hi):
        return self._lcmIn(lo, hi) if lo <= hi else 1

    # O(logN * logU expected) -- LCM (-1 once it passes cap) of the kFrom-th through kTo-th largest values; RANKS,
    # 1-indexed and inclusive:
    # (1, 1) is just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def lcmOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"lcmOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._lcmIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logN * logU expected) -- LCM (-1 once it passes cap) of the kFrom-th through kTo-th smallest values; RANKS,
    # 1-indexed and inclusive:
    # (1, 1) is just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def lcmOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"lcmOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._lcmIn(self._kth(kFrom), self._kth(kTo))

    # O(logN * logU expected) -- LCM (-1 once it passes cap) of the k largest values; k is a COUNT, not an index: k = 0
    # takes no values
    # (returns 1), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    # raises IndexError unless 0 <= k <= size
    def lcmOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"lcmOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._lcmGe(self._kth(self.n - k + 1)) if k else 1

    # O(logN * logU expected) -- LCM (-1 once it passes cap) of the values < x; 1 if there are none
    def lcmOfLtX(self, x):
        return self._lcmLe(x - 1)

    # O(logN * logU expected) -- LCM (-1 once it passes cap) of the values <= x; 1 if there are none
    def lcmOfLteX(self, x):
        return self._lcmLe(x)

    # O(logN * logU expected) -- LCM (-1 once it passes cap) of the k smallest values; k is a COUNT, not an index: k = 0
    # takes no values
    # (returns 1), k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
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

    # O(logN expected) -- how many copies of x (0 if x isn't there, e.g. on an empty set)
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values (0 if empty)
    def countDistinct(self):
        return self.d

    # O(logN expected) -- how many values > x (0 if there are none, e.g. on an empty set)
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(logN expected) -- how many values >= x (0 if there are none, e.g. on an empty set)
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(logN expected) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logN expected) -- how many values < x (0 if there are none, e.g. on an empty set)
    def countLtX(self, x):
        return self._lt(x)

    # O(logN expected) -- how many values <= x (0 if there are none, e.g. on an empty set)
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

    # O(1) -- largest value; raises IndexError if empty
    def max(self):
        if not self.n:
            raise IndexError("max: the set is empty")
        return self.mx

    # O(logN expected) -- upper median: the (floor(size/2) + 1)-th smallest value; raises IndexError if empty
    def medianHigh(self):
        if not self.n:
            raise IndexError("medianHigh: the set is empty")
        return self._kth((self.n >> 1) + 1)

    # O(logN expected) -- lower median: the ceil(size/2)-th smallest value; raises IndexError if empty
    def medianLow(self):
        if not self.n:
            raise IndexError("medianLow: the set is empty")
        return self._kth((self.n + 1) >> 1)

    # O(1) -- smallest value; raises IndexError if empty
    def min(self):
        if not self.n:
            raise IndexError("min: the set is empty")
        return self.mn

    # O(1) -- gcd of all values; 0 if empty
    def gcdOfAll(self):
        return self.G[self.root]

    # O(logN * logU expected) -- gcd of the values > x; 0 if there are none
    def gcdOfGtX(self, x):
        return self._gcdGe(x + 1)

    # O(logN * logU expected) -- gcd of the values >= x; 0 if there are none
    def gcdOfGteX(self, x):
        return self._gcdGe(x)

    # O(logN * logU expected) -- gcd of the values v with lo <= v <= hi; 0 if there are none
    def gcdOfInValRange(self, lo, hi):
        return self._gcdIn(lo, hi) if lo <= hi else 0

    # O(logN * logU expected) -- gcd of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive:
    # (1, 1) is just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def gcdOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"gcdOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._gcdIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logN * logU expected) -- gcd of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive:
    # (1, 1) is just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def gcdOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(
                f"gcdOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = "
                f"{self.n}")
        return self._gcdIn(self._kth(kFrom), self._kth(kTo))

    # O(logN * logU expected) -- gcd of the k largest values; k is a COUNT, not an index: k = 0 takes no values
    # (returns 0), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    # raises IndexError unless 0 <= k <= size
    def gcdOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"gcdOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._gcdGe(self._kth(self.n - k + 1)) if k else 0

    # O(logN * logU expected) -- gcd of the values < x; 0 if there are none
    def gcdOfLtX(self, x):
        return self._gcdLe(x - 1)

    # O(logN * logU expected) -- gcd of the values <= x; 0 if there are none
    def gcdOfLteX(self, x):
        return self._gcdLe(x)

    # O(logN * logU expected) -- gcd of the k smallest values; k is a COUNT, not an index: k = 0 takes no values
    # (returns 0), k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
    # raises IndexError unless 0 <= k <= size
    def gcdOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"gcdOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._gcdLe(self._kth(k)) if k else 0

    # O(logN * logU expected) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the
    # smallest (=
    # popMin()), pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logN * logU expected) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self.mx
        self._add(v, -1)
        return v

    # O(logN * logU expected) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self.mn
        self._add(v, -1)
        return v

    # O(logN * logU expected) -- remove one copy of x if present; returns how many were removed (0 or 1: 0 if x isn't
    # there, e.g. on an empty set)
    def remove(self, x):
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logN * logU expected) -- remove every copy of val; returns how many were removed (0 if val isn't there, e.g. on
    # an empty set)
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logN * logU expected) -- remove min(cnt, count(val)) copies of val; returns how many were removed (0 if val
    # isn't there, e.g. on an empty set)
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(logN * logU expected) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo
    # > hi)
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

    # O(logN expected) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logN expected) -- smallest value >= x; None if there is none
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

