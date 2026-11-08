# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/treap-with-xor-or-cachedmex-medians-mode/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow mex min mode orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
# @data-structure-type: treap
# @values: online
# @keys: numbers
# @tracks: medians mex mode
# @complexities:
#   add: log(N) expected
#   addCount: log(N) expected
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
#   medianHigh: 1
#   medianLow: 1
#   mex: 1
#   min: log(N) expected
#   mode: 1
#   orOfAll: 1
#   orOfGtX: log(N) expected
#   orOfGteX: log(N) expected
#   orOfInValRange: log(N) expected
#   orOfKthLargestRange: log(N) expected
#   orOfKthSmallestRange: log(N) expected
#   orOfLargestK: log(N) expected
#   orOfLtX: log(N) expected
#   orOfLteX: log(N) expected
#   orOfSmallestK: log(N) expected
#   pop: log(N) expected
#   popMax: log(N) expected
#   popMin: log(N) expected
#   remove: log(N) expected
#   removeAll: log(N) expected
#   removeCount: log(N) expected
#   removeInValRange: log(N) expected
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
#   node: key[1*N] cnt[1*N] size[1*N] dn[1*N] xor[1*N] or[1*N]
#   tags: none
#   other: children[2*N] prio[1*N]
#   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree
from random import getrandbits
from random import random


# Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
# its value, its copies, and the copies, xor, OR and distinct values in its subtree. Nodes live in parallel lists (a node
# pool; node 0 is the empty tree) and removed nodes are reused. Updates split around x and merge back.


class TreapMultiset:
    __slots__ = ("K", "C", "Z", "X", "O", "D", "P", "L", "R", "free", "root", "n", "lowV", "lowB", "lowC", "highV", "highB", "highC", "mexV", "bk", "bkAt", "fh", "fhAt", "xtotal", "salt", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z = [0], [0], [0]  # key, copies, copies below
        self.D = [0]  # distinct values below
        self.X = [0]  # xor of the values below with an odd count
        self.O = [0]  # OR of the values below
        self.P, self.L, self.R = [0.0], [0], [0]  # priority, children
        self.free = []  # removed nodes, reused first
        self.salt = getrandbits(60)  # hash containers key on salted values, so no fixed input can force collisions
        self.xtotal = 0  # xor of all values (copies count)
        self.bk, self.bkAt = {}, {}  # mode: count -> list of the values with that many copies; value -> its index there
        self.fh, self.fhAt = [], {}  # mode: max-heap of the counts that have a bucket; count -> its index in it
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
        self.O.append(0)
        self.P.append(random())
        self.L.append(0)
        self.R.append(0)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
        self.D[t] = self.D[l] + self.D[r] + 1
        self.X[t] = self.X[l] ^ self.X[r] ^ (self.K[t] if self.C[t] & 1 else 0)
        self.O[t] = self.O[l] | self.O[r] | self.K[t]

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
            self.O[q] = self.O[l] | self.O[r] | self.K[q]
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

    def _resetCached(self):  # nothing counted: as newly built
        self.mexV = 0
        self.bk, self.bkAt, self.fh, self.fhAt = {}, {}, [], {}
        self.n = self.d = 0
        self.xtotal = 0

    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)
        self.K = [0]
        self.C = [0]
        self.Z = [0]
        self.D = [0]
        self.X = [0]
        self.O = [0]
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

    def _orLe(self, x):  # OR of the values <= x
        K, F, L, R = self.K, self.O, self.L, self.R
        t, res = self.root, 0
        while t:
            if x < K[t]:
                t = L[t]
            else:
                res |= F[L[t]] | K[t]
                t = R[t]
        return res

    def _orGe(self, x):  # OR of the values >= x
        K, F, L, R = self.K, self.O, self.L, self.R
        t, res = self.root, 0
        while t:
            if K[t] < x:
                t = R[t]
            else:
                res |= F[R[t]] | K[t]
                t = L[t]
        return res

    def _orIn(self, lo, hi):  # OR of the values in [lo, hi] (lo <= hi)
        K, F, L, R = self.K, self.O, self.L, self.R
        t = self.root
        while t and not lo <= K[t] <= hi:  # down to the highest node inside [lo, hi]
            t = L[t] if hi < K[t] else R[t]
        if not t:
            return 0
        res = K[t]
        u = L[t]  # its left side is <= hi: keep what is >= lo
        while u:
            if lo <= K[u]:
                res |= K[u] | F[R[u]]
                u = L[u]
            else:
                u = R[u]
        u = R[t]  # its right side is >= lo: keep what is <= hi
        while u:
            if K[u] <= hi:
                res |= K[u] | F[L[u]]
                u = R[u]
            else:
                u = L[u]
        return res

    # O(logN expected) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logN expected) -- add cnt copies of val (nothing if cnt <= 0)
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
        return self.O[self.root]

    # O(logN expected) -- bitwise OR of the values > x; 0 if there are none
    def orOfGtX(self, x):
        return self._orGe(x + 1)

    # O(logN expected) -- bitwise OR of the values >= x; 0 if there are none
    def orOfGteX(self, x):
        return self._orGe(x)

    # O(logN expected) -- bitwise OR of the values v with lo <= v <= hi; 0 if there are none
    def orOfInValRange(self, lo, hi):
        return self._orIn(lo, hi) if lo <= hi else 0

    # O(logN expected) -- bitwise OR of the kFrom-th through kTo-th largest values; RANKS, 1-indexed and inclusive:
    # (1, 1) is just the largest, (5, 8) the 5th, 6th, 7th and 8th largest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._orIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logN expected) -- bitwise OR of the kFrom-th through kTo-th smallest values; RANKS, 1-indexed and inclusive:
    # (1, 1) is just the smallest, (2, 4) the 2nd, 3rd and 4th smallest, (1, size) every value (copies count); raises
    # IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._orIn(self._kth(kFrom), self._kth(kTo))

    # O(logN expected) -- bitwise OR of the k largest values; k is a COUNT, not an index: k = 0 takes no values
    # (returns 0), k = 1 just the largest, k = size every value (copies count: in {2, 5, 5}, k = 2 takes 5 and 5);
    # raises IndexError unless 0 <= k <= size
    def orOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orGe(self._kth(self.n - k + 1)) if k else 0

    # O(logN expected) -- bitwise OR of the values < x; 0 if there are none
    def orOfLtX(self, x):
        return self._orLe(x - 1)

    # O(logN expected) -- bitwise OR of the values <= x; 0 if there are none
    def orOfLteX(self, x):
        return self._orLe(x)

    # O(logN expected) -- bitwise OR of the k smallest values; k is a COUNT, not an index: k = 0 takes no values
    # (returns 0), k = 1 just the smallest, k = size every value (copies count: in {2, 2, 5}, k = 2 takes 2 and 2);
    # raises IndexError unless 0 <= k <= size
    def orOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orLe(self._kth(k)) if k else 0

    # O(logN expected) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (=
    # popMin()), pop(size - 1) the largest (copies count); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logN expected) -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.n:
            raise IndexError("popMax: the set is empty")
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(logN expected) -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.n:
            raise IndexError("popMin: the set is empty")
        v = self._kth(1)
        self._add(v, -1)
        return v

    # O(logN expected) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self._countOf(x):
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

    # O(logN expected) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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
