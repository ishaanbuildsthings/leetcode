# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/avl-with-and-medians/template.py
# @operations: add addCount andOfAll andOfGtX andOfGteX andOfInValRange andOfKthLargestRange andOfKthSmallestRange andOfLargestK andOfLtX andOfLteX andOfSmallestK clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow min pop popMax popMin remove removeAll removeCount removeInValRange size smallestGtX smallestGteX
# @data-structure-type: avl
# @values: online
# @keys: numbers
# @tracks: medians
# @complexities:
#   add: log(N)
#   addCount: log(N)
#   andOfAll: 1
#   andOfGtX: log(N)
#   andOfGteX: log(N)
#   andOfInValRange: log(N)
#   andOfKthLargestRange: log(N)
#   andOfKthSmallestRange: log(N)
#   andOfLargestK: log(N)
#   andOfLtX: log(N)
#   andOfLteX: log(N)
#   andOfSmallestK: log(N)
#   clear: N
#   count: log(N)
#   countDistinct: 1
#   countGtX: log(N)
#   countGteX: log(N)
#   countInValRange: log(N)
#   countLtX: log(N)
#   countLteX: log(N)
#   firstIndex: log(N)
#   kth: log(N)
#   largestLtX: log(N)
#   largestLteX: log(N)
#   lastIndex: log(N)
#   max: log(N)
#   medianHigh: 1
#   medianLow: 1
#   min: log(N)
#   pop: log(N)
#   popMax: log(N)
#   popMin: log(N)
#   remove: log(N)
#   removeAll: log(N)
#   removeCount: log(N)
#   removeInValRange: log(N) amortized
#   size: 1
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   build: 1
# @memory:
#   layout: none
#   node: key[1*N] cnt[1*N] size[1*N] and[1*N]
#   tags: none
#   other: children[2*N] height[1*N]
#   note: N = most distinct values present at once (removed nodes are reused). C++: each multiset owns its node pool; Python: parallel lists per tree

# Ordered multiset (online: any values, nothing known ahead): an AVL tree with one node per distinct value, so every
# operation is O(log N) worst case (height <= 1.44 log2 N). Each node keeps its value, its copies, and the copies, AND
# in its subtree. Nodes live in parallel lists (a node pool; node 0 is the empty tree) and removed
# nodes are reused.


class AVLMultiset:
    __slots__ = ("K", "C", "Z", "A", "H", "L", "R", "free", "root", "n", "lowV", "lowB", "lowC", "highV", "highB", "highC", "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z = [0], [0], [0]  # key, copies, copies below
        self.A = [-1]  # AND of the values below (the empty tree's: every bit)
        self.H, self.L, self.R = [0], [0], [0]  # height (empty tree 0), children
        self.free = []  # removed nodes, reused first
        self.root = self.n = self.d = 0

    def _new(self, x, c):
        if self.free:
            t = self.free.pop()
            self.K[t], self.C[t], self.L[t], self.R[t] = x, c, 0, 0
            return t
        self.K.append(x)
        self.C.append(c)
        self.Z.append(0)
        self.A.append(-1)
        self.H.append(0)
        self.L.append(0)
        self.R.append(0)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
        self.A[t] = self.A[l] & self.A[r] & self.K[t]
        hl, hr = self.H[l], self.H[r]
        self.H[t] = (hl if hl > hr else hr) + 1

    def _rotR(self, t):  # t's left child moves up
        L, R = self.L, self.R
        l = L[t]
        L[t], R[l] = R[l], t
        self._pull(t)
        self._pull(l)
        return l

    def _rotL(self, t):  # t's right child moves up
        L, R = self.L, self.R
        r = R[t]
        R[t], L[r] = L[r], t
        self._pull(t)
        self._pull(r)
        return r

    def _bal(self, t):  # pull t and restore |height(left) - height(right)| <= 1; returns the subtree's new root
        H, L, R = self.H, self.L, self.R
        self._pull(t)
        b = H[L[t]] - H[R[t]]
        if b > 1:
            if H[L[L[t]]] < H[R[L[t]]]:
                L[t] = self._rotL(L[t])
            return self._rotR(t)
        if b < -1:
            if H[R[R[t]]] < H[L[R[t]]]:
                R[t] = self._rotR(R[t])
            return self._rotL(t)
        return t

    def _popMin(self, t):  # (t without its smallest node, that node)
        if not self.L[t]:
            return self.R[t], t
        self.L[t], m = self._popMin(self.L[t])
        return self._bal(t), m

    def _ins(self, t, x, c):  # c copies of x into subtree t; returns its new root
        if not t:
            self.d += 1
            t = self._new(x, c)
            self._pull(t)
            return t
        K = self.K
        if x < K[t]:
            self.L[t] = self._ins(self.L[t], x, c)
        elif x > K[t]:
            self.R[t] = self._ins(self.R[t], x, c)
        else:
            self.C[t] += c
            if not self.C[t]:  # x is gone: replace its node by the smallest node on its right
                self.d -= 1
                self.free.append(t)
                l, r = self.L[t], self.R[t]
                if not l or not r:
                    return l or r
                r, m = self._popMin(r)
                self.L[m], self.R[m] = l, r
                return self._bal(m)
        return self._bal(t)

    def _insert(self, x, c):
        self.root = self._ins(self.root, x, c)

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


    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps both medians current
        self.n += c
        self._insert(x, c)
        n = self.n
        if c > 0:
            if n == c:  # the set was empty
                self.lowV = self.highV = x
                self.lowB = self.highB = 0
                self.lowC = self.highC = c
                return
        else:
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

    def _resetCached(self):  # nothing counted: as newly built
        self.n = self.d = 0

    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)
        self.K = [0]
        self.C = [0]
        self.Z = [0]
        self.H = [0]
        self.L = [0]
        self.R = [0]
        self.A = [-1]
        self.free = []
        self.root = 0

    def _andLe(self, x):  # AND of the values <= x
        K, F, L, R = self.K, self.A, self.L, self.R
        t, res = self.root, -1
        while t:
            if x < K[t]:
                t = L[t]
            else:
                res &= F[L[t]] & K[t]
                t = R[t]
        return res

    def _andGe(self, x):  # AND of the values >= x
        K, F, L, R = self.K, self.A, self.L, self.R
        t, res = self.root, -1
        while t:
            if K[t] < x:
                t = R[t]
            else:
                res &= F[R[t]] & K[t]
                t = L[t]
        return res

    def _andIn(self, lo, hi):  # AND of the values in [lo, hi] (lo <= hi)
        K, F, L, R = self.K, self.A, self.L, self.R
        t = self.root
        while t and not lo <= K[t] <= hi:  # down to the highest node inside [lo, hi]
            t = L[t] if hi < K[t] else R[t]
        if not t:
            return -1
        res = K[t]
        u = L[t]  # its left side is <= hi: keep what is >= lo
        while u:
            if lo <= K[u]:
                res &= K[u] & F[R[u]]
                u = L[u]
            else:
                u = R[u]
        u = R[t]  # its right side is >= lo: keep what is <= hi
        while u:
            if K[u] <= hi:
                res &= K[u] & F[L[u]]
                u = R[u]
            else:
                u = L[u]
        return res

    # O(logN) -- add one copy of x
    def add(self, x):
        self._add(x, 1)

    # O(logN) -- add cnt copies of val (nothing if cnt <= 0)
    def addCount(self, val, cnt):
        if cnt > 0:
            self._add(val, cnt)

    # O(1) -- bitwise AND of all values; -1 (every bit set) if empty
    def andOfAll(self):
        return self.A[self.root]

    # O(logN) -- bitwise AND of the values > x; -1 (every bit set) if there are none
    def andOfGtX(self, x):
        return self._andGe(x + 1)

    # O(logN) -- bitwise AND of the values >= x; -1 (every bit set) if there are none
    def andOfGteX(self, x):
        return self._andGe(x)

    # O(logN) -- bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none
    def andOfInValRange(self, lo, hi):
        return self._andIn(lo, hi) if lo <= hi else -1

    # O(logN) -- bitwise AND of the kFrom-th..kTo-th largest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def andOfKthLargestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"andOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._andIn(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))

    # O(logN) -- bitwise AND of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); raises IndexError unless 1 <= kFrom <= kTo <= size
    def andOfKthSmallestRange(self, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= self.n:
            raise IndexError(f"andOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}")
        return self._andIn(self._kth(kFrom), self._kth(kTo))

    # O(logN) -- bitwise AND of the k largest values (-1 (every bit set) for k = 0); raises IndexError unless 0 <= k <= size
    def andOfLargestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"andOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._andGe(self._kth(self.n - k + 1)) if k else -1

    # O(logN) -- bitwise AND of the values < x; -1 (every bit set) if there are none
    def andOfLtX(self, x):
        return self._andLe(x - 1)

    # O(logN) -- bitwise AND of the values <= x; -1 (every bit set) if there are none
    def andOfLteX(self, x):
        return self._andLe(x)

    # O(logN) -- bitwise AND of the k smallest values (-1 (every bit set) for k = 0); raises IndexError unless 0 <= k <= size
    def andOfSmallestK(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"andOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}")
        return self._andLe(self._kth(k)) if k else -1

    # O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    def clear(self):
        self._clearData()
        self._resetCached()

    # O(logN) -- how many copies of x
    def count(self, x):
        return self._countOf(x)

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(logN) -- how many values > x
    def countGtX(self, x):
        return self.n - self._le(x)

    # O(logN) -- how many values >= x
    def countGteX(self, x):
        return self.n - self._lt(x)

    # O(logN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    def countInValRange(self, lo, hi):
        return self._le(hi) - self._lt(lo) if lo <= hi else 0

    # O(logN) -- how many values < x
    def countLtX(self, x):
        return self._lt(x)

    # O(logN) -- how many values <= x
    def countLteX(self, x):
        return self._le(x)

    # O(logN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    def firstIndex(self, x):
        return self._lt(x) if self._countOf(x) else -1

    # O(logN) -- the value at sorted position i (0-indexed: kth(0) is the min); raises IndexError unless 0 <= i < size
    def kth(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"kth: needs 0 <= i < size, got i = {i}, size = {self.n}")
        return self._kth(i + 1)

    # O(logN) -- largest value < x; None if there is none
    def largestLtX(self, x):
        c = self._lt(x)
        return self._kth(c) if c else None

    # O(logN) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        c = self._le(x)
        return self._kth(c) if c else None

    # O(logN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    def lastIndex(self, x):
        return self._le(x) - 1 if self._countOf(x) else -1

    # O(logN) -- largest value; None if empty
    def max(self):
        return self._kth(self.n) if self.n else None

    # O(1) -- upper median: the (floor(size/2) + 1)-th smallest value; None if empty
    def medianHigh(self):
        return self.highV if self.n else None

    # O(1) -- lower median: the ceil(size/2)-th smallest value; None if empty
    def medianLow(self):
        return self.lowV if self.n else None

    # O(logN) -- smallest value; None if empty
    def min(self):
        return self._kth(1) if self.n else None

    # O(logN) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); raises IndexError unless 0 <= i < size
    def pop(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pop: needs 0 <= i < size, got i = {i}, size = {self.n}")
        v = self._kth(i + 1)
        self._add(v, -1)
        return v

    # O(logN) -- remove and return the largest value; None if empty
    def popMax(self):
        if not self.n:
            return None
        v = self._kth(self.n)
        self._add(v, -1)
        return v

    # O(logN) -- remove and return the smallest value; None if empty
    def popMin(self):
        if not self.n:
            return None
        v = self._kth(1)
        self._add(v, -1)
        return v

    # O(logN) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        if not self.count(x):
            return 0
        self._add(x, -1)
        return 1

    # O(logN) -- remove every copy of val; returns how many were removed
    def removeAll(self, val):
        k = self.count(val)
        if k:
            self._add(val, -k)
        return k

    # O(logN) -- remove min(cnt, count(val)) copies of val; returns how many were removed
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

    # O(logN) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        c = self._le(x)
        return self._kth(c + 1) if c < self.n else None

    # O(logN) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        c = self._lt(x)
        return self._kth(c + 1) if c < self.n else None
