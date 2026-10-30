# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/splay-with-xor-or-and-minmax-mode-gaps/template.py
# @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow min minAdjacentDiff mode orOfAll orOfGtX orOfGteX orOfInValRange orOfKthLargestRange orOfKthSmallestRange orOfLargestK orOfLtX orOfLteX orOfSmallestK pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX xorOfAll xorOfGtX xorOfGteX xorOfInValRange xorOfKthLargestRange xorOfKthSmallestRange xorOfLargestK xorOfLtX xorOfLteX xorOfSmallestK
# @data-structure-type: splay
# @values: online
# @keys: numbers
# @tracks: minmax mode gaps
# @complexities:
#   add: log(N) amortized
#   addCount: log(N) amortized
#   andOfAll: 1
#   andOfGtX: log(N) amortized
#   andOfGteX: log(N) amortized
#   andOfInValRange: log(N) amortized
#   andOfKthLargestRange: log(N) amortized
#   andOfKthSmallestRange: log(N) amortized
#   andOfLargestK: log(N) amortized
#   andOfLtX: log(N) amortized
#   andOfLteX: log(N) amortized
#   andOfSmallestK: log(N) amortized
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
#   max: 1
#   maxGap: 1 amortized
#   medianHigh: log(N) amortized
#   medianLow: log(N) amortized
#   min: 1
#   minAdjacentDiff: 1 amortized
#   mode: 1
#   orOfAll: 1
#   orOfGtX: log(N) amortized
#   orOfGteX: log(N) amortized
#   orOfInValRange: log(N) amortized
#   orOfKthLargestRange: log(N) amortized
#   orOfKthSmallestRange: log(N) amortized
#   orOfLargestK: log(N) amortized
#   orOfLtX: log(N) amortized
#   orOfLteX: log(N) amortized
#   orOfSmallestK: log(N) amortized
#   pop: log(N) amortized
#   popMax: log(N) amortized
#   popMin: log(N) amortized
#   remove: log(N) amortized
#   removeAll: log(N) amortized
#   removeCount: log(N) amortized
#   removeInValRange: log(N) amortized
#   size: 1
#   smallestGtX: log(N) amortized
#   smallestGteX: log(N) amortized
#   xorOfAll: 1
#   xorOfGtX: log(N) amortized
#   xorOfGteX: log(N) amortized
#   xorOfInValRange: log(N) amortized
#   xorOfKthLargestRange: log(N) amortized
#   xorOfKthSmallestRange: log(N) amortized
#   xorOfLargestK: log(N) amortized
#   xorOfLtX: log(N) amortized
#   xorOfLteX: log(N) amortized
#   xorOfSmallestK: log(N) amortized
#   build: 1
# @memory:
#   layout: none
#   node: key[1*N] cnt[1*N] size[1*N] xor[1*N] or[1*N] and[1*N]
#   tags: none
#   other: children[2*N] parent[1*N]
#   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree
from heapq import heappop, heappush

# Ordered multiset (online: any values, nothing known ahead): a splay tree with one node per distinct value. Each node
# keeps its value, its copies, and the copies, xor, OR, AND in its subtree; every operation splays the
# last node it touched to the root, which makes each one O(log N) amortized. Nodes live in parallel lists (a node pool;
# node 0 is the empty tree) and removed nodes are reused.


class SplayMultiset:
    __slots__ = ("K", "C", "Z", "X", "O", "A", "L", "R", "P", "free", "root", "n", "mn", "mx", "bk", "maxF", "gc", "gmin", "gmax", "dups", "xtotal", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z = [0], [0], [0]  # key, copies, copies below
        self.X = [0]  # xor of the values below with an odd count
        self.O = [0]  # OR of the values below
        self.A = [-1]  # AND of the values below (the empty tree's: every bit)
        self.L, self.R, self.P = [0], [0], [0]  # children, parent
        self.free = []  # removed nodes, reused first
        self.xtotal = 0  # xor of all values (copies count)
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies
        self.bk, self.maxF = {}, 0  # mode: count -> the values with that many copies; the highest count
        self.root = self.n = self.d = 0

    def _new(self, x, parent):
        if self.free:
            t = self.free.pop()
            self.K[t], self.C[t], self.L[t], self.R[t], self.P[t] = x, 0, 0, 0, parent
            return t
        self.K.append(x)
        self.C.append(0)
        self.Z.append(0)
        self.X.append(0)
        self.O.append(0)
        self.A.append(-1)
        self.L.append(0)
        self.R.append(0)
        self.P.append(parent)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
        self.X[t] = self.X[l] ^ self.X[r] ^ (self.K[t] if self.C[t] & 1 else 0)
        self.O[t] = self.O[l] | self.O[r] | self.K[t]
        self.A[t] = self.A[l] & self.A[r] & self.K[t]

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
    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies)
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t, before = self.root, 0
        while True:
            l = L[t]
            zl = before + Z[l]
            if k <= zl:
                t = l
            elif k <= zl + C[t]:
                res = K[t], zl, C[t]
                self._touch(t)
                return res
            else:
                before = zl + C[t]
                t = R[t]

    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max current
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
        self.bk, self.maxF = {}, 0
        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0
        self.n = self.d = 0
        self.xtotal = 0

    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)
        self.K = [0]
        self.C = [0]
        self.Z = [0]
        self.X = [0]
        self.O = [0]
        self.L = [0]
        self.R = [0]
        self.P = [0]
        self.A = [-1]
        self.free = []
        self.root = 0

    def _xlt(self, x):  # xor of the values < x (copies count)
        K, C, X, L, R = self.K, self.C, self.X, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if K[t] < x:
                res ^= X[L[t]] ^ (K[t] if C[t] & 1 else 0)
                t = R[t]
            else:
                t = L[t]
        self._touch(last)
        return res

    def _xle(self, x):  # xor of the values <= x (copies count)
        K, C, X, L, R = self.K, self.C, self.X, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if x < K[t]:
                t = L[t]
            else:
                res ^= X[L[t]] ^ (K[t] if C[t] & 1 else 0)
                t = R[t]
        self._touch(last)
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
                self._touch(t)
                return res ^ X[l] ^ (K[t] if (k - zl) & 1 else 0)
            else:
                k -= zl + C[t]
                res ^= X[l] ^ (K[t] if C[t] & 1 else 0)
                t = R[t]

    def _orLe(self, x):  # OR of the values <= x
        K, F, L, R = self.K, self.O, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if x < K[t]:
                t = L[t]
            else:
                res |= F[L[t]] | K[t]
                t = R[t]
        self._touch(last)
        return res

    def _orGe(self, x):  # OR of the values >= x
        K, F, L, R = self.K, self.O, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if K[t] < x:
                t = R[t]
            else:
                res |= F[R[t]] | K[t]
                t = L[t]
        self._touch(last)
        return res

    def _orIn(self, lo, hi):  # OR of the values in [lo, hi] (lo <= hi)
        K, F, L, R = self.K, self.O, self.L, self.R
        t = self.root
        last = 0
        while t and not lo <= K[t] <= hi:  # down to the highest node inside [lo, hi]
            last = t
            t = L[t] if hi < K[t] else R[t]
        if not t:
            self._touch(last)
            return 0
        res = K[t]
        a, na = t, 0
        u = L[t]  # its left side is <= hi: keep what is >= lo
        while u:
            a, na = u, na + 1
            if lo <= K[u]:
                res |= K[u] | F[R[u]]
                u = L[u]
            else:
                u = R[u]
        b, nb = t, 0
        u = R[t]  # its right side is >= lo: keep what is <= hi
        while u:
            b, nb = u, nb + 1
            if K[u] <= hi:
                res |= K[u] | F[L[u]]
                u = R[u]
            else:
                u = L[u]
        self._touch(a if na >= nb else b)  # the end of the longer path pays for both
        return res

    def _andLe(self, x):  # AND of the values <= x
        K, F, L, R = self.K, self.A, self.L, self.R
        t, res, last = self.root, -1, 0
        while t:
            last = t
            if x < K[t]:
                t = L[t]
            else:
                res &= F[L[t]] & K[t]
                t = R[t]
        self._touch(last)
        return res

    def _andGe(self, x):  # AND of the values >= x
        K, F, L, R = self.K, self.A, self.L, self.R
        t, res, last = self.root, -1, 0
        while t:
            last = t
            if K[t] < x:
                t = R[t]
            else:
                res &= F[R[t]] & K[t]
                t = L[t]
        self._touch(last)
        return res

    def _andIn(self, lo, hi):  # AND of the values in [lo, hi] (lo <= hi)
        K, F, L, R = self.K, self.A, self.L, self.R
        t = self.root
        last = 0
        while t and not lo <= K[t] <= hi:  # down to the highest node inside [lo, hi]
            last = t
            t = L[t] if hi < K[t] else R[t]
        if not t:
            self._touch(last)
            return -1
        res = K[t]
        a, na = t, 0
        u = L[t]  # its left side is <= hi: keep what is >= lo
        while u:
            a, na = u, na + 1
            if lo <= K[u]:
                res &= K[u] & F[R[u]]
                u = L[u]
            else:
                u = R[u]
        b, nb = t, 0
        u = R[t]  # its right side is >= lo: keep what is <= hi
        while u:
            b, nb = u, nb + 1
            if K[u] <= hi:
                res &= K[u] & F[L[u]]
                u = R[u]
            else:
                u = L[u]
        self._touch(a if na >= nb else b)  # the end of the longer path pays for both
        return res

    # O(logN amortized) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logN amortized) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1) -- bitwise AND of all values; -1 (every bit set) if empty
    def andOfAll(self):
        return self.A[self.root]

    # O(logN amortized) -- bitwise AND of the values > x; -1 (every bit set) if there are none
    def andOfGtX(self, x):
        return self._andGe(x + 1)

    # O(logN amortized) -- bitwise AND of the values >= x; -1 (every bit set) if there are none
    def andOfGteX(self, x):
        return self._andGe(x)

    # O(logN amortized) -- bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none
    def andOfInValRange(self, lo, hi):
        return self._andIn(lo, hi) if lo <= hi else -1

    # O(logN amortized) -- bitwise AND of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def andOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"andOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._andIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logN amortized) -- bitwise AND of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def andOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"andOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._andIn(self._kth(kFrom), self._kth(kTo))

    # O(logN amortized) -- bitwise AND of the k largest values (-1 (every bit set) for k = 0); raises IndexError unless 0 <= k <= size
    def andOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"andOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._andGe(self._kth(self.n - k + 1)) if k else -1

    # O(logN amortized) -- bitwise AND of the values < x; -1 (every bit set) if there are none
    def andOfLtX(self, x):
        return self._andLe(x - 1)

    # O(logN amortized) -- bitwise AND of the values <= x; -1 (every bit set) if there are none
    def andOfLteX(self, x):
        return self._andLe(x)

    # O(logN amortized) -- bitwise AND of the k smallest values (-1 (every bit set) for k = 0); raises IndexError unless 0 <= k <= size
    def andOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"andOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._andLe(self._kth(k)) if k else -1

    # O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logN amortized) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(logN amortized) -- how many values > x
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(logN amortized) -- how many values >= x
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(logN amortized) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logN amortized) -- how many values < x
    def countLtX(self, x):
        return self._lt(x)

    # O(logN amortized) -- how many values <= x
    def countLteX(self, x):
        return self._le(x)

    # O(logN amortized) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(logN amortized) -- the value at sorted position i (0-indexed: kth(0) is the min); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1)

    # O(logN amortized) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(logN amortized) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        c = self._le(x)
        return self._kth(c) if c else None

    # O(logN amortized) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(1) -- largest value; None if empty
    def max(self):
        return self.mx if self.n else None

    # O(1 amortized) -- largest difference between two neighbouring distinct values; None if fewer than 2 distinct values
    def maxGap(self):
        return self._maxGap() if self.d >= 2 else None

    # O(logN amortized) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        return self._kth((self.n >> 1) + 1) if self.n else None

    # O(logN amortized) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        return self._kth((self.n + 1) >> 1) if self.n else None

    # O(1) -- smallest value; None if empty
    def min(self):
        return self.mn if self.n else None

    # O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); None if fewer than 2 values
    def minAdjacentDiff(self):
        if self.n < 2:
            return None
        return 0 if self.dups else self._minGap()

    # O(1) -- (a most frequent value, its count); None if empty. C++ returns the smallest of the most frequent values
    def mode(self):
        if not self.n:
            return None
        f = self.maxF
        return next(iter(self.bk[f])), f

    # O(1) -- bitwise OR of all values; 0 if empty
    def orOfAll(self):
        return self.O[self.root]

    # O(logN amortized) -- bitwise OR of the values > x; 0 if there are none
    def orOfGtX(self, x):
        return self._orGe(x + 1)

    # O(logN amortized) -- bitwise OR of the values >= x; 0 if there are none
    def orOfGteX(self, x):
        return self._orGe(x)

    # O(logN amortized) -- bitwise OR of the values v with lo <= v <= hi; 0 if there are none
    def orOfInValRange(self, lo, hi):
        return self._orIn(lo, hi) if lo <= hi else 0

    # O(logN amortized) -- bitwise OR of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"orOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._orIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logN amortized) -- bitwise OR of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def orOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"orOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._orIn(self._kth(kFrom), self._kth(kTo))

    # O(logN amortized) -- bitwise OR of the k largest values (0 for k = 0); raises IndexError unless 0 <= k <= size
    def orOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orGe(self._kth(self.n - k + 1)) if k else 0

    # O(logN amortized) -- bitwise OR of the values < x; 0 if there are none
    def orOfLtX(self, x):
        return self._orLe(x - 1)

    # O(logN amortized) -- bitwise OR of the values <= x; 0 if there are none
    def orOfLteX(self, x):
        return self._orLe(x)

    # O(logN amortized) -- bitwise OR of the k smallest values (0 for k = 0); raises IndexError unless 0 <= k <= size
    def orOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"orOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._orLe(self._kth(k)) if k else 0

    # O(logN amortized) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logN amortized) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self.mx
        self._add(v, -1)
        return v

    # O(logN amortized) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self.mn
        self._add(v, -1)
        return v

    # O(logN amortized) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self.count(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logN amortized) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logN amortized) -- remove min(cnt, count(val)) copies of val; returns how many were removed
    def removeCount(self, val, cnt):
        k = min(cnt, self.count(val))
        if k <= 0:
            return 0
        self._add(val, -k)
        return k

    # O(logN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
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

    # O(logN amortized) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logN amortized) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None

    # O(1) -- xor of all values (copies count: a value with an even count cancels out); 0 if empty
    def xorOfAll(self):
        return self.xtotal

    # O(logN amortized) -- xor of the values > x (copies count)
    def xorOfGtX(self, x):
        return self.xtotal ^ self._xle(x)

    # O(logN amortized) -- xor of the values >= x (copies count)
    def xorOfGteX(self, x):
        return self.xtotal ^ self._xlt(x)

    # O(logN amortized) -- xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)
    def xorOfInValRange(self, lo, hi):
        return self._xle(hi) ^ self._xlt(lo) if lo <= hi else 0

    # O(logN amortized) -- xor of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def xorOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._xorFirst(self.n - kFrom + 1) ^ self._xorFirst(self.n - kTo)

    # O(logN amortized) -- xor of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def xorOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._xorFirst(kTo) ^ self._xorFirst(kFrom - 1)

    # O(logN amortized) -- xor of the k largest values (copies count); raises IndexError unless 0 <= k <= size
    def xorOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self.xtotal ^ self._xorFirst(self.n - k)

    # O(logN amortized) -- xor of the values < x (copies count)
    def xorOfLtX(self, x):
        return self._xlt(x)

    # O(logN amortized) -- xor of the values <= x (copies count)
    def xorOfLteX(self, x):
        return self._xle(x)

    # O(logN amortized) -- xor of the k smallest values (copies count); raises IndexError unless 0 <= k <= size
    def xorOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"xorOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._xorFirst(k)
