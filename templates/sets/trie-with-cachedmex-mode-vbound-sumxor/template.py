# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/trie-with-cachedmex-mode-vbound-sumxor/template.py
# @operations: add addCount clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX countXorGtK countXorGteK countXorLtK countXorLteK firstIndex kth kthXor largestLtX largestLteX largestXorLtK largestXorLteK lastIndex max maxXorAgainstX maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM medianHigh medianLow mex mexXor min minXorAgainstX minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM mode pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX smallestXorGtK smallestXorGteK sumAll sumXor
# @data-structure-type: trie
# @values: online-bits
# @keys: numbers
# @tracks: vbound sumxor mex mode
# @complexities:
#   add: log(U)
#   addCount: log(U)
#   clear: 1 amortized
#   count: log(U)
#   countDistinct: 1
#   countDistinctInValRange: log(U)
#   countGtX: log(U)
#   countGteX: log(U)
#   countInValRange: log(U)
#   countLtX: log(U)
#   countLteX: log(U)
#   countXorGtK: log(U)
#   countXorGteK: log(U)
#   countXorLtK: log(U)
#   countXorLteK: log(U)
#   firstIndex: log(U)
#   kth: log(U)
#   kthXor: log(U)
#   largestLtX: log(U)
#   largestLteX: log(U)
#   largestXorLtK: log(U)
#   largestXorLteK: log(U)
#   lastIndex: log(U)
#   max: 1
#   maxXorAgainstX: log(U)
#   maxXorWithVGtM: log(U)
#   maxXorWithVGteM: log(U)
#   maxXorWithVInValRange: log(U)
#   maxXorWithVLtM: log(U)
#   maxXorWithVLteM: log(U)
#   medianHigh: log(U)
#   medianLow: log(U)
#   mex: 1
#   mexXor: log(U)
#   min: 1
#   minXorAgainstX: log(U)
#   minXorWithVGtM: log(U)
#   minXorWithVGteM: log(U)
#   minXorWithVInValRange: log(U)
#   minXorWithVLtM: log(U)
#   minXorWithVLteM: log(U)
#   mode: 1
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
#   smallestXorGtK: log(U)
#   smallestXorGteK: log(U)
#   sumAll: log(U)
#   sumXor: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: c[1*log(U)] p[1*log(U)] mn[1*log(U)] mx[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per add of a new value, one node per bit of its path; U = 2^bits. Each multiset owns its nodes (clear() keeps the arrays' capacity)

# Ordered multiset of integers in [0, 2^bits) as a binary trie: one level per bit, highest bit first; each node keeps
# how many copies, how many distinct values, the smallest and largest value are below it. Besides the usual ordered queries it answers questions
# about v ^ x over every value v (max / min / k-th / counts / closest to a bound / limits on v, sum, mex) by walking one bit
# per level, so O(bits) each. Nodes live in parallel lists (node 0 = empty, node 1 = the root) and are never removed.


class TrieMultiset:
    __slots__ = ("B", "top", "L", "R", "C", "P", "MN", "MX", "bc", "n", "mexV", "bk", "maxF", "d")

    # O(1) -- an empty multiset for integers in [0, 2^bits) (bits = 30 holds values up to 1073741823)
    def __init__(self, bits):
        self.B = bits
        self.top = (1 << bits) - 1  # the largest value it can hold
        self.L, self.R, self.C = [0, 0], [0, 0], [0, 0]  # child for bit 0 / bit 1, copies below; node 0 = empty, 1 = root
        self.P = [0, 0]  # distinct values below
        self.MN, self.MX = [0, 0], [0, 0]  # smallest / largest value below (meaningful while its count > 0)
        self.bc = [0] * bits  # bc[h] = copies with bit h set
        self.bk, self.maxF = {}, 0  # mode: count -> the values with that many copies; the highest count
        self.mexV = 0  # the mex, kept current (0 for the empty set)
        self.n = self.d = 0

    def _new(self):  # a new empty node
        self.L.append(0)
        self.R.append(0)
        self.C.append(0)
        self.P.append(0)
        self.MN.append(0)
        self.MX.append(0)
        return len(self.C) - 1

    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)
        self.L, self.R, self.C = [0, 0], [0, 0], [0, 0]
        self.P = [0, 0]
        self.MN, self.MX = [0, 0], [0, 0]
        self.bc = [0] * self.B

    def _insert(self, x, c):  # c copies of x; returns x's new count
        L, R, C = self.L, self.R, self.C
        bc = self.bc
        t = 1
        C[1] += c
        path = [1]
        for h in range(self.B - 1, -1, -1):
            if x >> h & 1:
                bc[h] += c
                u = R[t]
                if not u:
                    u = R[t] = self._new()
            else:
                u = L[t]
                if not u:
                    u = L[t] = self._new()
            t = u
            C[t] += c
            path.append(t)
        f = C[t]
        if not f or f == c:  # x appeared or disappeared
            self.d += 1 if f else -1
            P, g = self.P, 1 if f else -1
            for u in path:
                P[u] += g
            MN, MX = self.MN, self.MX
            if f:
                MN[t] = MX[t] = x
            for u in reversed(path[:-1]):  # from the bottom: what is present below each node changed
                l, r = L[u], R[u]
                MN[u] = MN[l] if C[l] else MN[r]
                MX[u] = MX[r] if C[r] else MX[l]
        return f

    def _cntLt(self, b, key):  # copies whose stored value ^ key is < b
        if b <= 0:
            return 0
        if b > self.top:
            return self.n
        L, R, C = self.L, self.R, self.C
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            kb = key >> h & 1
            if b >> h & 1:  # everything below the child with result bit 0 is < b
                res += C[R[t] if kb else L[t]]
                t = L[t] if kb else R[t]
            else:
                t = R[t] if kb else L[t]
            if not t:
                break
        return res

    def _kthX(self, k, key):  # the k-th smallest (1-indexed) stored value ^ key
        L, R, C = self.L, self.R, self.C
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            if key >> h & 1:
                z, o = R[t], L[t]
            else:
                z, o = L[t], R[t]
            if k <= C[z]:
                t = z
            else:
                k -= C[z]
                t = o
                res |= 1 << h
        return res

    def _extreme(self, t, h, key, big):  # bits h..0 of the largest (big) / smallest stored value ^ key below node t
        L, R, C = self.L, self.R, self.C
        res = 0
        while h >= 0:
            p = (key >> h & 1) ^ big  # the child whose result bit is 1 (big) / 0
            u = R[t] if p else L[t]
            if C[u]:
                t = u
                if big:
                    res |= 1 << h
            else:
                t = L[t] if p else R[t]
                if not big:
                    res |= 1 << h
            h -= 1
        return res

    def _lt(self, x):
        return self._cntLt(x, 0)

    def _le(self, x):
        return self._cntLt(x + 1, 0)

    def _countOf(self, x):
        if not 0 <= x <= self.top:
            return 0
        L, R = self.L, self.R
        t = 1
        for h in range(self.B - 1, -1, -1):
            t = R[t] if x >> h & 1 else L[t]
            if not t:
                return 0
        return self.C[t]

    def _kth(self, k):
        return self._kthX(k, 0)

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies)
        L, R, C = self.L, self.R, self.C
        t, v, before = 1, 0, 0
        for h in range(self.B - 1, -1, -1):
            l = L[t]
            if before + C[l] < k:
                before += C[l]
                t = R[t]
                v |= 1 << h
            else:
                t = l
        return v, before, C[t]

    def _mexX(self, key):  # smallest m >= 0 with no value stored as m ^ key
        L, R, P = self.L, self.R, self.P
        if P[1] > self.top:  # every value is present
            return self.top + 1
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            if key >> h & 1:
                z, o = R[t], L[t]
            else:
                z, o = L[t], R[t]
            if P[z] == 1 << h:  # that half is full: the answer has bit h set
                res |= 1 << h
                t = o
            else:
                t = z
            if not t:
                break
        return res

    def _findMex(self):
        return self._mexX(0)

    def _distinctLt(self, x):  # distinct values < x
        if x <= 0:
            return 0
        if x > self.top:
            return self.d
        L, R, P = self.L, self.R, self.P
        key = 0
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            kb = key >> h & 1
            if x >> h & 1:
                res += P[R[t] if kb else L[t]]
                t = L[t] if kb else R[t]
            else:
                t = R[t] if kb else L[t]
            if not t:
                break
        return res

    def _sumX(self, key):  # sum of stored value ^ key over every copy: bit by bit from the per-bit counts
        bc, n, res = self.bc, self.n, 0
        for h in range(self.B):
            res += (n - bc[h] if key >> h & 1 else bc[h]) << h
        return res

    def _bestIn(self, x, lo, hi, big):  # the largest (big) / smallest v ^ x over the values v in [lo, hi]; None if none
        lo, hi = max(lo, 0), min(hi, self.top)
        if lo > hi:
            return None
        L, R, C = self.L, self.R, self.C
        t, h = 1, self.B - 1
        while h >= 0 and (lo >> h & 1) == (hi >> h & 1):  # the bits lo and hi share: one path
            t = R[t] if lo >> h & 1 else L[t]
            h -= 1
        if not C[t]:
            return None
        if h < 0:  # lo == hi, present
            return lo ^ x
        # where they split, the left child only needs v >= lo and the right child only v <= hi
        a = self._bestSide(L[t], h - 1, x, lo, True, big)
        b = self._bestSide(R[t], h - 1, x, hi, False, big)
        if a is None or b is None:
            return b if a is None else a
        return max(a, b) if big else min(a, b)

    def _bestSide(self, t, h, x, bound, ge, big):  # best v ^ x below node t with v >= bound (ge) / v <= bound
        L, R, C, MN, MX = self.L, self.R, self.C, self.MN, self.MX
        if not C[t] or (MX[t] < bound if ge else MN[t] > bound):
            return None
        while h >= 0:
            p = (x >> h & 1) ^ big  # the child whose bit of v ^ x is 1 (big) / 0
            u = R[t] if p else L[t]
            if C[u] and (MX[u] >= bound if ge else MN[u] <= bound):
                t = u
            else:
                t = L[t] if p else R[t]
            h -= 1
        return MN[t] ^ x

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps the mex current
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
            if x == self.mexV:  # x filled the mex
                self.mexV = self._findMex()
        else:
            if 0 <= x < self.mexV and not f:  # the last copy of a value below the mex
                self.mexV = x

    def _resetCached(self):  # nothing counted: as newly built
        self.mexV = 0
        self.bk, self.maxF = {}, 0
        self.n = self.d = 0

    # O(logU) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logU) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1 amortized) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
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

    # O(logU) -- how many values v have v ^ x > k
    def countXorGtK(self, x, k):
        return self.n - self._cntLt(k + 1, x)

    # O(logU) -- how many values v have v ^ x >= k
    def countXorGteK(self, x, k):
        return self.n - self._cntLt(k, x)

    # O(logU) -- how many values v have v ^ x < k
    def countXorLtK(self, x, k):
        return self._cntLt(k, x)

    # O(logU) -- how many values v have v ^ x <= k
    def countXorLteK(self, x, k):
        return self._cntLt(k + 1, x)

    # O(logU) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(logU) -- the value at sorted position i (0-indexed: kth(0) is the min); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1)

    # O(logU) -- the i-th smallest v ^ x over the values v (0-indexed, copies count); raises IndexError unless 0 <= i < size
    def kthXor(self, x, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kthXor: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kthX(i + 1, x)

    # O(logU) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(logU) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        c = self._le(x)
        return self._kth(c) if c else None

    # O(logU) -- largest v ^ x that is < k; None if there is none
    def largestXorLtK(self, x, k):
        key = x
        c = self._cntLt(k, key)
        return self._kthX(c, key) if c else None

    # O(logU) -- largest v ^ x that is <= k; None if there is none
    def largestXorLteK(self, x, k):
        key = x
        c = self._cntLt(k + 1, key)
        return self._kthX(c, key) if c else None

    # O(logU) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(1) -- largest value; None if empty
    def max(self):
        if not self.n:
            return None
        return self.MX[1]

    # O(logU) -- largest v ^ x over the values v in the set; None if the set is empty (needs 0 <= x < 2^bits)
    def maxXorAgainstX(self, x):
        if not self.n:
            return None
        return self._extreme(1, self.B - 1, x, True)

    # O(logU) -- largest v ^ x over the values v > m; None if there is none
    def maxXorWithVGtM(self, x, m):
        return self._bestIn(x, m + 1, self.top, True)

    # O(logU) -- largest v ^ x over the values v >= m; None if there is none
    def maxXorWithVGteM(self, x, m):
        return self._bestIn(x, m, self.top, True)

    # O(logU) -- largest v ^ x over the values v with lo <= v <= hi; None if there is none
    def maxXorWithVInValRange(self, x, lo, hi):
        return self._bestIn(x, lo, hi, True)

    # O(logU) -- largest v ^ x over the values v < m; None if there is none
    def maxXorWithVLtM(self, x, m):
        return self._bestIn(x, 0, m - 1, True)

    # O(logU) -- largest v ^ x over the values v <= m; None if there is none
    def maxXorWithVLteM(self, x, m):
        return self._bestIn(x, 0, m, True)

    # O(logU) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        return self._kth((self.n >> 1) + 1) if self.n else None

    # O(logU) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        return self._kth((self.n + 1) >> 1) if self.n else None

    # O(1) -- smallest non-negative integer not in the set
    def mex(self):
        return self.mexV

    # O(logU) -- smallest non-negative integer that is not v ^ x for any value v
    def mexXor(self, x):
        return self._mexX(x)

    # O(1) -- smallest value; None if empty
    def min(self):
        if not self.n:
            return None
        return self.MN[1]

    # O(logU) -- smallest v ^ x over the values v in the set; None if the set is empty (needs 0 <= x < 2^bits)
    def minXorAgainstX(self, x):
        if not self.n:
            return None
        return self._extreme(1, self.B - 1, x, False)

    # O(logU) -- smallest v ^ x over the values v > m; None if there is none
    def minXorWithVGtM(self, x, m):
        return self._bestIn(x, m + 1, self.top, False)

    # O(logU) -- smallest v ^ x over the values v >= m; None if there is none
    def minXorWithVGteM(self, x, m):
        return self._bestIn(x, m, self.top, False)

    # O(logU) -- smallest v ^ x over the values v with lo <= v <= hi; None if there is none
    def minXorWithVInValRange(self, x, lo, hi):
        return self._bestIn(x, lo, hi, False)

    # O(logU) -- smallest v ^ x over the values v < m; None if there is none
    def minXorWithVLtM(self, x, m):
        return self._bestIn(x, 0, m - 1, False)

    # O(logU) -- smallest v ^ x over the values v <= m; None if there is none
    def minXorWithVLteM(self, x, m):
        return self._bestIn(x, 0, m, False)

    # O(1) -- (a most frequent value, its count); None if empty. C++ returns the smallest of the most frequent values
    def mode(self):
        if not self.n:
            return None
        f = self.maxF
        return next(iter(self.bk[f])), f

    # O(logU) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logU) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self.MX[1]
        self._add(v, -1)
        return v

    # O(logU) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self.MN[1]
        self._add(v, -1)
        return v

    # O(logU) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self.count(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logU) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logU) -- remove min(cnt, count(val)) copies of val; returns how many were removed
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

    # O(logU) -- smallest v ^ x that is > k; None if there is none
    def smallestXorGtK(self, x, k):
        key = x
        c = self._cntLt(k + 1, key)
        return self._kthX(c + 1, key) if c < self.n else None

    # O(logU) -- smallest v ^ x that is >= k; None if there is none
    def smallestXorGteK(self, x, k):
        key = x
        c = self._cntLt(k, key)
        return self._kthX(c + 1, key) if c < self.n else None

    # O(logU) -- sum of all values
    def sumAll(self):
        return self._sumX(0)

    # O(logU) -- sum of v ^ x over every value v (copies count)
    def sumXor(self, x):
        return self._sumX(x)
