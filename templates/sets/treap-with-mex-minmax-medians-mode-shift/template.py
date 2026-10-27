# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/treap-with-mex-minmax-medians-mode-shift/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min mode pop popMax popMin remove removeAll removeCount removeInValRange shiftAll size smallestGtX smallestGteX
# @data-structure-type: treap
# @values: online
# @keys: numbers
# @tracks: minmax medians mode shift
# @complexities:
#   add: log(N) expected
#   addCount: log(N) expected
#   clear: N
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
#   max: 1
#   medianHigh: 1
#   medianLow: 1
#   mex: log(N) expected
#   min: 1
#   mode: 1
#   pop: log(N) expected
#   popMax: log(N) expected
#   popMin: log(N) expected
#   remove: log(N) expected
#   removeAll: log(N) expected
#   removeCount: log(N) expected
#   removeInValRange: log(N) expected
#   shiftAll: 1
#   size: 1
#   smallestGtX: log(N) expected
#   smallestGteX: log(N) expected
#   build: 1
# @memory:
#   layout: none
#   node: key[1*N] cnt[1*N] size[1*N] dn[1*N]
#   tags: none
#   other: children[2*N] prio[1*N]
#   note: N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, call resetPool() between test cases; Python: parallel lists per tree
from random import random


# Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
# its value, its copies, and the copies and distinct values in its subtree. Nodes live in parallel lists (a node
# pool; node 0 is the empty tree) and removed nodes are reused. Updates split around x and merge back.


class TreapMultiset:
    __slots__ = ("K", "C", "Z", "D", "P", "L", "R", "free", "root", "n", "mn", "mx", "lowV", "lowB", "lowC", "highV", "highB", "highC", "bk", "maxF", "off", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z = [0], [0], [0]  # key, copies, copies below
        self.D = [0]  # distinct values below
        self.P, self.L, self.R = [0.0], [0], [0]  # priority, children
        self.free = []  # removed nodes, reused first
        self.off = 0  # every value v is stored as v - off: shiftAll only moves off
        self.bk, self.maxF = {}, 0  # mode: count -> the values with that many copies; the highest count
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
        self.P.append(random())
        self.L.append(0)
        self.R.append(0)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
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

    def _insert(self, x, c):
        a, b = self._split(self.root, x)
        m, b = self._splitLe(b, x)  # m: the node of x, or 0
        if not m:
            m = self._new(x)
            self.d += 1
        f = self.C[m] = self.C[m] + c
        if f:
            self._pull(m)
        else:
            self.free.append(m)
            m = 0
            self.d -= 1
        self.root = self._merge(self._merge(a, m), b)
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
        base = -self.off  # (stored as v - off: the real values >= 0 are the stored ones >= -off)
        c0 = self._distinctLt(base)
        t, before, res = self.root, -c0, self.d - c0  # before: distinct values >= 0 left of t's subtree
        while t:
            j = before + D[L[t]]
            if K[t] < base or K[t] == base + j:
                before = j + 1
                t = R[t]
            else:
                res = j
                t = L[t]
        return base + res  # (a stored value)

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max, both medians current
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

    def _resetCached(self):  # nothing counted: as newly built
        self.bk, self.maxF = {}, 0
        self.n = self.d = 0
        self.off = 0

    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)
        self.K = [0]
        self.C = [0]
        self.Z = [0]
        self.D = [0]
        self.L = [0]
        self.R = [0]
        self.P = [0.0]
        self.free = []
        self.root = 0

    # O(logN expected) -- add one copy of x
    def add(self, x):
        x -= self.off
        self._add(x, 1)

    # O(logN expected) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        val -= self.off
        if cnt > 0:
            self._add(val, cnt)

    # O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logN expected) -- how many copies of x
    def count(self, x):
        x -= self.off
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(logN expected) -- how many distinct values v with lo <= v <= hi (0 if lo > hi)
    def countDistinctInValRange(self, lo, hi):
        lo -= self.off
        hi -= self.off
        if lo > hi:
            return 0
        return self._distinctLt(hi) - self._distinctLt(lo) + (1 if self._countOf(hi) else 0)

    # O(logN expected) -- how many values > x
    def countGtX(self, x):
        x -= self.off
        return self.n - self._le(x)

    # O(logN expected) -- how many values >= x
    def countGteX(self, x):
        x -= self.off
        return self.n - self._lt(x)

    # O(logN expected) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        lo -= self.off
        hi -= self.off
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logN expected) -- how many values < x
    def countLtX(self, x):
        x -= self.off
        return self._lt(x)

    # O(logN expected) -- how many values <= x
    def countLteX(self, x):
        x -= self.off
        return self._le(x)

    # O(logN expected) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    def firstIndex(self, x):
        x -= self.off
        return self._lt(x) if self._countOf(x) else -1

    # O(logN expected) -- the value at sorted position i (0-indexed: kth(0) is the min); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1) + self.off

    # O(logN expected) -- largest value < x; None if there is none
    def largestLtX(self, x):
        x -= self.off
        c = self._lt(x)
        return self._kth(c) + self.off if c else None

    # O(logN expected) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        x -= self.off
        c = self._le(x)
        return self._kth(c) + self.off if c else None

    # O(logN expected) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    def lastIndex(self, x):
        x -= self.off
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(1) -- largest value; None if empty
    def max(self):
        return self.mx + self.off if self.n else None

    # O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        return self.highV + self.off if self.n else None

    # O(1) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        return self.lowV + self.off if self.n else None

    # O(logN expected) -- smallest non-negative integer not in the set
    def mex(self):
        return self._findMex() + self.off

    # O(1) -- smallest value; None if empty
    def min(self):
        return self.mn + self.off if self.n else None

    # O(1) -- (a most frequent value, its count); None if empty. C++ returns the smallest of the most frequent values
    def mode(self):
        if not self.n:
            return None
        f = self.maxF
        return next(iter(self.bk[f])) + self.off, f

    # O(logN expected) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v + self.off

    # O(logN expected) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self.mx
        self._add(v, -1)
        return v + self.off

    # O(logN expected) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self.mn
        self._add(v, -1)
        return v + self.off

    # O(logN expected) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        x -= self.off
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logN expected) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        val -= self.off
        k = self._countOf(val)
        if k:
            self._add(val, -k)
        return k

    # O(logN expected) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        val -= self.off
        k = min(cnt, self._countOf(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(logN expected) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    def removeInValRange(self, lo, hi):
        lo -= self.off
        hi -= self.off
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

    # O(1) -- add d to every value (d may be negative)
    def shiftAll(self, d):
        self.off += d

    # O(1) -- how many values (copies count)
    def size(self):
        return self.n

    # O(1) -- same as size()
    def __len__(self):
        return self.n

    # O(logN expected) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        x -= self.off
        c = self._le(x)
        return self._kth(c + 1) + self.off if c < self.n else None

    # O(logN expected) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        x -= self.off
        c = self._lt(x)
        return self._kth(c + 1) + self.off if c < self.n else None
