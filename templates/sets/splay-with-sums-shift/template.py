# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/splay-with-sums-shift/template.py
# @operations: add addCount clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow min pop popMax popMin remove removeAll removeCount removeInValRange shiftAll size smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: splay
# @values: online
# @keys: numbers
# @tracks: shift
# @complexities:
#   add: log(N) amortized
#   addCount: log(N) amortized
#   clear: N
#   count: log(N) amortized
#   countDistinct: 1
#   countGtX: log(N) amortized
#   countGteX: log(N) amortized
#   countInValRange: log(N) amortized
#   countLtX: log(N) amortized
#   countLteX: log(N) amortized
#   firstIndex: log(N) amortized
#   kth: log(N) amortized
#   largestLtX: log(N) amortized
#   largestLteX: log(N) amortized
#   lastIndex: log(N) amortized
#   max: log(N) amortized
#   medianHigh: log(N) amortized
#   medianLow: log(N) amortized
#   min: log(N) amortized
#   pop: log(N) amortized
#   popMax: log(N) amortized
#   popMin: log(N) amortized
#   remove: log(N) amortized
#   removeAll: log(N) amortized
#   removeCount: log(N) amortized
#   removeInValRange: log(N) amortized
#   shiftAll: 1
#   size: 1
#   smallestGtX: log(N) amortized
#   smallestGteX: log(N) amortized
#   sumAbsDiffToMedian: log(N) amortized
#   sumAbsDiffToX: log(N) amortized
#   sumAll: 1
#   sumGtX: log(N) amortized
#   sumGteX: log(N) amortized
#   sumInValRange: log(N) amortized
#   sumKthLargestRange: log(N) amortized
#   sumKthSmallestRange: log(N) amortized
#   sumLargestK: log(N) amortized
#   sumLtX: log(N) amortized
#   sumLteX: log(N) amortized
#   sumSmallestK: log(N) amortized
#   build: 1
# @memory:
#   layout: none
#   node: key[1*N] cnt[1*N] size[1*N] sum[1*N]
#   tags: none
#   other: children[2*N] parent[1*N]
#   note: N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, call resetPool() between test cases; Python: parallel lists per tree

# Ordered multiset (online: any values, nothing known ahead): a splay tree with one node per distinct value. Each node
# keeps its value, its copies, and the copies, sum in its subtree; every operation splays the
# last node it touched to the root, which makes each one O(log N) amortized. Nodes live in parallel lists (a node pool;
# node 0 is the empty tree) and removed nodes are reused.


class SplayMultiset:
    __slots__ = ("K", "C", "Z", "S", "L", "R", "P", "free", "root", "n", "off", "total", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z, self.S = [0], [0], [0], [0]  # key, copies, copies below, sum below
        self.L, self.R, self.P = [0], [0], [0]  # children, parent
        self.free = []  # removed nodes, reused first
        self.off = 0  # every value v is stored as v - off: shiftAll only moves off
        self.root = self.n = self.total = self.d = 0

    def _new(self, x, parent):
        if self.free:
            t = self.free.pop()
            self.K[t], self.C[t], self.L[t], self.R[t], self.P[t] = x, 0, 0, 0, parent
            return t
        self.K.append(x)
        self.C.append(0)
        self.Z.append(0)
        self.S.append(0)
        self.L.append(0)
        self.R.append(0)
        self.P.append(parent)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
        self.S[t] = self.S[l] + self.S[r] + self.C[t] * self.K[t]

    def _rotate(self, x):  # x moves above its parent
        L, R, P = self.L, self.R, self.P
        p = P[x]
        g = P[p]
        if L[p] == x:
            b = R[x]
            L[p], R[x] = b, p
        else:
            b = L[x]
            R[p], L[x] = b, p
        if b:
            P[b] = p
        P[p], P[x] = x, g
        if g:
            if L[g] == p:
                L[g] = x
            else:
                R[g] = x
        self._pull(p)
        self._pull(x)

    def _splay(self, x):  # x becomes the root of its tree
        P, L = self.P, self.L
        while P[x]:
            p = P[x]
            g = P[p]
            if g:
                self._rotate(p if (L[g] == p) == (L[p] == x) else x)
            self._rotate(x)
        return x

    def _touch(self, t):
        if t:
            self.root = self._splay(t)

    def _insert(self, x, c):
        K, L, R = self.K, self.L, self.R
        t = self.root
        while t and K[t] != x:
            nxt = L[t] if x < K[t] else R[t]
            if not nxt:
                break
            t = nxt
        if t and K[t] == x:  # x is already here
            f = self.C[t] = self.C[t] + c
            self._pull(t)
            self.root = self._splay(t)
            if not f:
                self._erase(t)
            return f  # (x's new count)
        u = self._new(x, t)
        self.C[u] = c
        self._pull(u)
        if t:
            if x < K[t]:
                L[t] = u
            else:
                R[t] = u
        self.root = self._splay(u)
        self.d += 1
        return c

    def _erase(self, t):  # t is the root
        L, R, P = self.L, self.R, self.P
        l, r = L[t], R[t]
        if l:
            P[l] = 0
        if r:
            P[r] = 0
        if not l:
            self.root = r
        else:
            m = l
            while R[m]:
                m = R[m]
            m = self._splay(m)  # the largest key on the left becomes the left tree's root, with no right child
            R[m] = r
            if r:
                P[r] = m
            self._pull(m)
            self.root = m
        self.free.append(t)
        self.d -= 1

    def _lt(self, x):  # copies of values < x
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if K[t] < x:
                res += Z[L[t]] + C[t]
                t = R[t]
            else:
                t = L[t]
        self._touch(last)
        return res

    def _le(self, x):  # copies of values <= x
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if x < K[t]:
                t = L[t]
            else:
                res += Z[L[t]] + C[t]
                t = R[t]
        self._touch(last)
        return res

    def _countOf(self, x):
        K, L, R = self.K, self.L, self.R
        t, last = self.root, 0
        while t and K[t] != x:
            last = t
            t = L[t] if x < K[t] else R[t]
        self._touch(t or last)
        return self.C[t]

    def _slt(self, x):  # sum of the values < x
        K, C, S, L, R = self.K, self.C, self.S, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if K[t] < x:
                res += S[L[t]] + C[t] * K[t]
                t = R[t]
            else:
                t = L[t]
        self._touch(last)
        return res

    def _sle(self, x):  # sum of the values <= x
        K, C, S, L, R = self.K, self.C, self.S, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if x < K[t]:
                t = L[t]
            else:
                res += S[L[t]] + C[t] * K[t]
                t = R[t]
        self._touch(last)
        return res

    def _kth(self, k):
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t = self.root
        while True:
            zl = Z[L[t]]
            if k <= zl:
                t = L[t]
            elif k <= zl + C[t]:
                self._touch(t)
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
                res = K[t], zl, C[t], acc + S[l]
                self._touch(t)
                return res
            else:
                before = zl + C[t]
                acc += S[l] + C[t] * K[t]
                t = R[t]

    def _add(self, x, c):  # c copies of x (c < 0 removes)
        self.n += c
        self.total += c * x
        self._insert(x, c)

    def _sumFirst(self, k):  # sum of the k smallest values
        if k <= 0:
            return 0
        v, b, _, s = self._kthInfo(k)
        return s + (k - b) * v

    def _resetCached(self):  # nothing counted: as newly built
        self.n = self.d = 0
        self.total = 0
        self.off = 0

    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)
        self.K = [0]
        self.C = [0]
        self.Z = [0]
        self.S = [0]
        self.L = [0]
        self.R = [0]
        self.P = [0]
        self.free = []
        self.root = 0

    # O(logN amortized) -- add one copy of x
    def add(self, x):
        x -= self.off
        self._add(x, 1)

    # O(logN amortized) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        val -= self.off
        if cnt > 0:
            self._add(val, cnt)

    # O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logN amortized) -- how many copies of x
    def count(self, x):
        x -= self.off
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(logN amortized) -- how many values > x
    def countGtX(self, x):
        x -= self.off
        return self.n - self._le(x)

    # O(logN amortized) -- how many values >= x
    def countGteX(self, x):
        x -= self.off
        return self.n - self._lt(x)

    # O(logN amortized) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        lo -= self.off
        hi -= self.off
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logN amortized) -- how many values < x
    def countLtX(self, x):
        x -= self.off
        return self._lt(x)

    # O(logN amortized) -- how many values <= x
    def countLteX(self, x):
        x -= self.off
        return self._le(x)

    # O(logN amortized) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    def firstIndex(self, x):
        x -= self.off
        return self._lt(x) if self._countOf(x) else -1

    # O(logN amortized) -- the value at sorted position i (0-indexed: kth(0) is the min); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1) + self.off

    # O(logN amortized) -- largest value < x; None if there is none
    def largestLtX(self, x):
        x -= self.off
        c = self._lt(x)
        return self._kth(c) + self.off if c else None

    # O(logN amortized) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        x -= self.off
        c = self._le(x)
        return self._kth(c) + self.off if c else None

    # O(logN amortized) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    def lastIndex(self, x):
        x -= self.off
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(logN amortized) -- largest value; None if empty
    def max(self):
        return self._kth(self.n) + self.off if self.n else None

    # O(logN amortized) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        return self._kth((self.n >> 1) + 1) + self.off if self.n else None

    # O(logN amortized) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        return self._kth((self.n + 1) >> 1) + self.off if self.n else None

    # O(logN amortized) -- smallest value; None if empty
    def min(self):
        return self._kth(1) + self.off if self.n else None

    # O(logN amortized) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v + self.off

    # O(logN amortized) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self._kth(self.n)
        self._add(v, -1)
        return v + self.off

    # O(logN amortized) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self._kth(1)
        self._add(v, -1)
        return v + self.off

    # O(logN amortized) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        x -= self.off
        if not self._countOf(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logN amortized) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        val -= self.off
        k = self._countOf(val)
        if k:
            self._add(val, -k)
        return k

    # O(logN amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        val -= self.off
        k = min(cnt, self._countOf(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(logN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    # O(logN amortized) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        x -= self.off
        c = self._le(x)
        return self._kth(c + 1) + self.off if c < self.n else None

    # O(logN amortized) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        x -= self.off
        c = self._lt(x)
        return self._kth(c + 1) + self.off if c < self.n else None

    # O(logN amortized) -- sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty
    def sumAbsDiffToMedian(self):
        if not self.n:
            return 0
        v, b, c, s = self._kthInfo((self.n + 1) >> 1)
        return v * b - s + (self.total - s - c * v) - v * (self.n - b - c)

    # O(logN amortized) -- sum of |v - x| over all values
    def sumAbsDiffToX(self, x):
        x -= self.off
        c, s = self._lt(x), self._slt(x)
        return x * c - s + (self.total - s) - x * (self.n - c)

    # O(1) -- sum of all values
    def sumAll(self):
        return self.total + self.off * self.n

    # O(logN amortized) -- sum of the values > x
    def sumGtX(self, x):
        x -= self.off
        return self.total - self._sle(x) + self.off * (self.n - self._le(x))

    # O(logN amortized) -- sum of the values >= x
    def sumGteX(self, x):
        x -= self.off
        return self.total - self._slt(x) + self.off * (self.n - self._lt(x))

    # O(logN amortized) -- sum of the values v with lo <= v <= hi (0 if lo > hi)
    def sumInValRange(self, lo, hi):
        if lo > hi:
            return 0
        lo -= self.off
        hi -= self.off
        return self._sle(hi) - self._slt(lo) + self.off * (self._le(hi) - self._lt(lo))

    # O(logN amortized) -- sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); raises IndexError unless 1 <= kFrom <= kTo <= size
    def sumKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._sumFirst(self.n - kFrom + 1) - self._sumFirst(self.n - kTo) + self.off * (kTo - kFrom + 1)

    # O(logN amortized) -- sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def sumKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._sumFirst(kTo) - self._sumFirst(kFrom - 1) + self.off * (kTo - kFrom + 1)

    # O(logN amortized) -- sum of the k largest values; raises IndexError unless 0 <= k <= size
    def sumLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.total - self._sumFirst(self.n - k) + self.off * k

    # O(logN amortized) -- sum of the values < x
    def sumLtX(self, x):
        x -= self.off
        return self._slt(x) + self.off * self._lt(x)

    # O(logN amortized) -- sum of the values <= x
    def sumLteX(self, x):
        x -= self.off
        return self._sle(x) + self.off * self._le(x)

    # O(logN amortized) -- sum of the k smallest values; raises IndexError unless 0 <= k <= size
    def sumSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._sumFirst(k) + self.off * k
