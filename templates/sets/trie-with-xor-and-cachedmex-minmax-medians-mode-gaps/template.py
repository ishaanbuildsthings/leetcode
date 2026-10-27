# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/trie-with-xor-and-cachedmex-minmax-medians-mode-gaps/template.py
# @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countDistinctInValRange countGtX countGteX countInValRange countLtX countLteX countXorGtK countXorGteK countXorLtK countXorLteK firstIndex kth kthXor largestLtX largestLteX largestXorLtK largestXorLteK lastIndex max maxGap maxXorAgainstX maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM medianHigh medianLow mex mexXor min minAdjacentDiff minXorAgainstX minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM mode pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX smallestXorGtK smallestXorGteK xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
# @data-structure-type: trie
# @values: online-bits
# @keys: numbers
# @tracks: minmax medians mex mode gaps
# @complexities:
#   add: log(U)
#   addCount: log(U)
#   andOfAll: 1
#   andOfGtX: log(U)
#   andOfGteX: log(U)
#   andOfInValRange: log(U)
#   andOfKthLargestRange: log(U)
#   andOfKthSmallestRange: log(U)
#   andOfLargestK: log(U)
#   andOfLtX: log(U)
#   andOfLteX: log(U)
#   andOfSmallestK: log(U)
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
#   maxGap: 1 amortized
#   maxXorAgainstX: log(U)
#   maxXorWithVGtM: log(U)*log(U)
#   maxXorWithVGteM: log(U)*log(U)
#   maxXorWithVInValRange: log(U)*log(U)
#   maxXorWithVLtM: log(U)*log(U)
#   maxXorWithVLteM: log(U)*log(U)
#   medianHigh: 1
#   medianLow: 1
#   mex: 1
#   mexXor: log(U)
#   min: 1
#   minAdjacentDiff: 1 amortized
#   minXorAgainstX: log(U)
#   minXorWithVGtM: log(U)*log(U)
#   minXorWithVGteM: log(U)*log(U)
#   minXorWithVInValRange: log(U)*log(U)
#   minXorWithVLtM: log(U)*log(U)
#   minXorWithVLteM: log(U)*log(U)
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
#   node: c[1*log(U)] p[1*log(U)] xor[1*log(U)] and[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per add of a new value, one node per bit of its path; U = 2^bits. Each multiset owns its nodes (clear() keeps the arrays' capacity)
from heapq import heappop, heappush

# Ordered multiset of integers in [0, 2^bits) as a binary trie: one level per bit, highest bit first; each node keeps
# how many copies, how many distinct values, their xor, their AND are below it. Besides the usual ordered queries it answers questions
# about v ^ x over every value v (max / min / k-th / counts / closest to a bound / limits on v, mex) by walking one bit
# per level, so O(bits) each. Nodes live in parallel lists (node 0 = empty, node 1 = the root) and are never removed.


class TrieMultiset:
    __slots__ = ("B", "top", "L", "R", "C", "P", "X", "A", "n", "mn", "mx", "lowV", "lowB", "lowC", "highV", "highB", "highC", "mexV", "bk", "maxF", "gc", "gmin", "gmax", "dups", "xtotal", "d")

    # O(1) -- an empty multiset for integers in [0, 2^bits) (bits = 30 holds values up to 1073741823)
    def __init__(self, bits):
        self.B = bits
        self.top = (1 << bits) - 1  # the largest value it can hold
        self.L, self.R, self.C = [0, 0], [0, 0], [0, 0]  # child for bit 0 / bit 1, copies below; node 0 = empty, 1 = root
        self.P = [0, 0]  # distinct values below
        self.X = [0, 0]  # xor of the stored values below with an odd count
        self.A = [-1, -1]  # AND of the values below (an empty node's: every bit)
        self.xtotal = 0  # xor of all values (copies count)
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.bk, self.maxF = {}, 0  # mode: count -> the values with that many copies; the highest count
        self.mexV = 0  # the mex, kept current (0 for the empty set)
        self.n = self.d = 0

    def _new(self):  # a new empty node
        self.L.append(0)
        self.R.append(0)
        self.C.append(0)
        self.P.append(0)
        self.X.append(0)
        self.A.append(-1)
        return len(self.C) - 1

    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)
        self.L, self.R, self.C = [0, 0], [0, 0], [0, 0]
        self.P = [0, 0]
        self.X = [0, 0]
        self.A = [-1, -1]

    def _insert(self, x, c):  # c copies of x; returns x's new count
        L, R, C = self.L, self.R, self.C
        X, xv = self.X, x if c & 1 else 0  # (with an odd c the stored value flips in or out of each xor on its path)
        t = 1
        C[1] += c
        X[1] ^= xv
        path = [1]
        for h in range(self.B - 1, -1, -1):
            if x >> h & 1:
                u = R[t]
                if not u:
                    u = R[t] = self._new()
            else:
                u = L[t]
                if not u:
                    u = L[t] = self._new()
            t = u
            C[t] += c
            X[t] ^= xv
            path.append(t)
        f = C[t]
        if not f or f == c:  # x appeared or disappeared
            self.d += 1 if f else -1
            P, g = self.P, 1 if f else -1
            for u in path:
                P[u] += g
            A = self.A
            A[t] = x if f else -1
            for u in reversed(path[:-1]):  # from the bottom: what is present below each node changed
                l, r = L[u], R[u]
                A[u] = A[l] & A[r]
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

    def _bestIn(self, x, lo, hi, big):  # the largest (big) / smallest v ^ x over the values v in [lo, hi]; None if none
        lo, hi = max(lo, 0), min(hi, self.top)
        if lo > hi:
            return None
        L, R, C = self.L, self.R, self.C
        mk = 0
        key = x ^ mk  # v ^ x = stored value ^ key
        best = None
        stack = [(1, 1 << self.B, 0)]  # (node, how many values it spans, the first of them)
        while stack:
            t, size, a = stack.pop()
            if not C[t] or a > hi or a + size - 1 < lo:
                continue
            if lo <= a and a + size - 1 <= hi:  # wholly inside: the best of this subtree
                v = a ^ x if size == 1 else ((a ^ x) & -size) | self._extreme(t, size.bit_length() - 2, key, big)
                if best is None or (v > best if big else v < best):
                    best = v
                continue
            half = size >> 1
            h = half.bit_length() - 1
            if mk >> h & 1:  # the stored child for v's bit h = 0 is the bit-1 child
                stack.append((R[t], half, a))
                stack.append((L[t], half, a + half))
            else:
                stack.append((L[t], half, a))
                stack.append((R[t], half, a + half))
        return best

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max, both medians, the mex current
        self.n += c
        if c & 1:  # an odd number of copies flips x in or out of the xor of everything
            self.xtotal ^= x
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
        if (g >= 2) != (f >= 2):  # values with 2+ copies (then the smallest difference is 0)
            self.dups += 1 if f >= 2 else -1
        if not g or not f:  # x appeared or disappeared: the gap between its neighbours splits or comes back
            p, q = self.largestLtX(x), self.smallestGtX(x)
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
            if 0 <= x < self.mexV and not f:  # the last copy of a value below the mex
                self.mexV = x
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

    def _gap(self, g, c):  # one more (c = 1) / fewer (c = -1) gap of size g
        gc = self.gc
        k = gc.get(g, 0) + c
        if k:
            gc[g] = k
            if k == 1 and c > 0:  # (a size already present has an entry in both heaps)
                if len(self.gmin) > 2 * len(gc) + 8:  # mostly sizes no longer present: rebuild from the live ones
                    self.gmin = sorted(gc)
                    self.gmax = [-v for v in reversed(self.gmin)]
                else:
                    heappush(self.gmin, g)
                    heappush(self.gmax, -g)
        else:
            del gc[g]

    def _minGap(self):  # heap tops of sizes no longer present are dropped as they surface
        h, gc = self.gmin, self.gc
        while h[0] not in gc:
            heappop(h)
        return h[0]

    def _maxGap(self):
        h, gc = self.gmax, self.gc
        while -h[0] not in gc:
            heappop(h)
        return -h[0]

    def _resetCached(self):  # nothing counted: as newly built
        self.mexV = 0
        self.bk, self.maxF = {}, 0
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0
        self.n = self.d = 0
        self.xtotal = 0

    def _xlt(self, x):  # xor of the values < x (copies count)
        if x <= 0:
            return 0
        if x > self.top:
            return self.xtotal
        L, R, X = self.L, self.R, self.X
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            if x >> h & 1:
                res ^= X[L[t]]
                t = R[t]
            else:
                t = L[t]
            if not t:
                break
        return res

    def _xle(self, x):
        return self._xlt(x + 1)

    def _xorFirst(self, k):  # xor of the k smallest values (copies count)
        if k <= 0:
            return 0
        L, R, C, X = self.L, self.R, self.C, self.X
        t, res, y = 1, 0, 0  # y: the stored value of the leaf reached
        for h in range(self.B - 1, -1, -1):
            l = L[t]
            if k <= C[l]:
                t = l
            else:
                k -= C[l]
                res ^= X[l]
                t = R[t]
                y |= 1 << h
        if k & 1:  # k copies of the leaf's value left
            res ^= y
        return res

    def _andIn(self, lo, hi):  # AND of the values in [lo, hi]
        lo, hi = max(lo, 0), min(hi, self.top)
        if lo > hi:
            return -1
        L, R, F = self.L, self.R, self.A
        t, h = 1, self.B - 1
        while h >= 0 and (lo >> h & 1) == (hi >> h & 1):  # the bits lo and hi share: one path
            t = R[t] if lo >> h & 1 else L[t]
            h -= 1
        if h < 0 or not t:
            return F[t]
        res = -1
        u = L[t]  # where they split, the left child only needs v >= lo
        for g in range(h - 1, -1, -1):
            if not u:
                break
            if lo >> g & 1:
                u = R[u]
            else:
                res &= F[R[u]]
                u = L[u]
        res &= F[u]
        u = R[t]  # and the right child only v <= hi
        for g in range(h - 1, -1, -1):
            if not u:
                break
            if hi >> g & 1:
                res &= F[L[u]]
                u = R[u]
            else:
                u = L[u]
        return res & F[u]

    def _andLe(self, x):  # AND of the values <= x
        return self._andIn(0, x)

    def _andGe(self, x):  # AND of the values >= x
        return self._andIn(x, self.top)

    # O(logU) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logU) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1) -- bitwise AND of all values; -1 (every bit set) if empty
    def andOfAll(self):
        return self.A[1]

    # O(logU) -- bitwise AND of the values > x; -1 (every bit set) if there are none
    def andOfGtX(self, x):
        return self._andGe(x + 1)

    # O(logU) -- bitwise AND of the values >= x; -1 (every bit set) if there are none
    def andOfGteX(self, x):
        return self._andGe(x)

    # O(logU) -- bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none
    def andOfInValRange(self, lo, hi):
        return self._andIn(lo, hi) if lo <= hi else -1

    # O(logU) -- bitwise AND of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def andOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"andOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._andIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logU) -- bitwise AND of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def andOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"andOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._andIn(self._kth(kFrom), self._kth(kTo))

    # O(logU) -- bitwise AND of the k largest values (-1 (every bit set) for k = 0); raises IndexError unless 0 <= k <= size
    def andOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"andOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._andGe(self._kth(self.n - k + 1)) if k else -1

    # O(logU) -- bitwise AND of the values < x; -1 (every bit set) if there are none
    def andOfLtX(self, x):
        return self._andLe(x - 1)

    # O(logU) -- bitwise AND of the values <= x; -1 (every bit set) if there are none
    def andOfLteX(self, x):
        return self._andLe(x)

    # O(logU) -- bitwise AND of the k smallest values (-1 (every bit set) for k = 0); raises IndexError unless 0 <= k <= size
    def andOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"andOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._andLe(self._kth(k)) if k else -1

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
        return self.mx if self.n else None

    # O(1 amortized) -- largest difference between two neighbouring distinct values; None if fewer than 2 distinct values
    def maxGap(self):
        return self._maxGap() if self.d >= 2 else None

    # O(logU) -- largest v ^ x over the values v in the set; None if the set is empty (needs 0 <= x < 2^bits)
    def maxXorAgainstX(self, x):
        if not self.n:
            return None
        return self._extreme(1, self.B - 1, x, True)

    # O(logU logU) -- largest v ^ x over the values v > m; None if there is none
    def maxXorWithVGtM(self, x, m):
        return self._bestIn(x, m + 1, self.top, True)

    # O(logU logU) -- largest v ^ x over the values v >= m; None if there is none
    def maxXorWithVGteM(self, x, m):
        return self._bestIn(x, m, self.top, True)

    # O(logU logU) -- largest v ^ x over the values v with lo <= v <= hi; None if there is none
    def maxXorWithVInValRange(self, x, lo, hi):
        return self._bestIn(x, lo, hi, True)

    # O(logU logU) -- largest v ^ x over the values v < m; None if there is none
    def maxXorWithVLtM(self, x, m):
        return self._bestIn(x, 0, m - 1, True)

    # O(logU logU) -- largest v ^ x over the values v <= m; None if there is none
    def maxXorWithVLteM(self, x, m):
        return self._bestIn(x, 0, m, True)

    # O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        return self.highV if self.n else None

    # O(1) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        return self.lowV if self.n else None

    # O(1) -- smallest non-negative integer not in the set
    def mex(self):
        return self.mexV

    # O(logU) -- smallest non-negative integer that is not v ^ x for any value v
    def mexXor(self, x):
        return self._mexX(x)

    # O(1) -- smallest value; None if empty
    def min(self):
        return self.mn if self.n else None

    # O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); None if fewer than 2 values
    def minAdjacentDiff(self):
        if self.n < 2:
            return None
        return 0 if self.dups else self._minGap()

    # O(logU) -- smallest v ^ x over the values v in the set; None if the set is empty (needs 0 <= x < 2^bits)
    def minXorAgainstX(self, x):
        if not self.n:
            return None
        return self._extreme(1, self.B - 1, x, False)

    # O(logU logU) -- smallest v ^ x over the values v > m; None if there is none
    def minXorWithVGtM(self, x, m):
        return self._bestIn(x, m + 1, self.top, False)

    # O(logU logU) -- smallest v ^ x over the values v >= m; None if there is none
    def minXorWithVGteM(self, x, m):
        return self._bestIn(x, m, self.top, False)

    # O(logU logU) -- smallest v ^ x over the values v with lo <= v <= hi; None if there is none
    def minXorWithVInValRange(self, x, lo, hi):
        return self._bestIn(x, lo, hi, False)

    # O(logU logU) -- smallest v ^ x over the values v < m; None if there is none
    def minXorWithVLtM(self, x, m):
        return self._bestIn(x, 0, m - 1, False)

    # O(logU logU) -- smallest v ^ x over the values v <= m; None if there is none
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
        v = self.mx
        self._add(v, -1)
        return v

    # O(logU) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self.mn
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

    # O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    def xorOfAll(self):
        return self.xtotal

    # O(logU) -- xor of the values > x (copies count)
    def xorOfGtX(self, x):
        return self.xtotal ^ self._xle(x)

    # O(logU) -- xor of the values >= x (copies count)
    def xorOfGteX(self, x):
        return self.xtotal ^ self._xlt(x)

    # O(logU) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    def xorOfInValRange(self, lo, hi):
        return self._xle(hi) ^ self._xlt(lo) if lo <= hi else 0

    # O(logU) -- xor of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def xorOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._xorFirst(self.n - kFrom + 1) ^ self._xorFirst(self.n - kTo)

    # O(logU) -- xor of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def xorOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._xorFirst(kTo) ^ self._xorFirst(kFrom - 1)

    # O(logU) -- xor of the k largest values (copies count); raises IndexError unless 0 <= k <= size
    def xorOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.xtotal ^ self._xorFirst(self.n - k)

    # O(logU) -- xor of the values < x (copies count)
    def xorOfLtX(self, x):
        return self._xlt(x)

    # O(logU) -- xor of the values <= x (copies count)
    def xorOfLteX(self, x):
        return self._xle(x)

    # O(logU) -- xor of the k smallest values (copies count); raises IndexError unless 0 <= k <= size
    def xorOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._xorFirst(k)
