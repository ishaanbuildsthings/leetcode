# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/bit-of-trees-order-stats-sums/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences getAll kthSmallest largestLtX largestLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: bit-of-trees
# @complexities:
#   countGtX: log(N)*log(U)
#   countGteX: log(N)*log(U)
#   countInValRange: log(N)*log(U)
#   countLtX: log(N)*log(U)
#   countLteX: log(N)*log(U)
#   countOccurrences: log(N)*log(U)
#   getAll: N
#   kthSmallest: log(N)*log(U)
#   largestLtX: log(N)*log(U)
#   largestLteX: log(N)*log(U)
#   pointAdd: log(N)*log(U)
#   pointAssign: log(N)*log(U)
#   pointChmax: log(N)*log(U)
#   pointChmin: log(N)*log(U)
#   pointGet: 1
#   rangeMax: log(N)*log(U)
#   rangeMin: log(N)*log(U)
#   rangeSum: log(N)*log(U)
#   smallestGtX: log(N)*log(U)
#   smallestGteX: log(N)*log(U)
#   sumAbsDiffToX: log(N)*log(U)
#   sumGtX: log(N)*log(U)
#   sumGteX: log(N)*log(U)
#   sumInValRange: log(N)*log(U)
#   sumKthLargestRange: log(N)*log(U)
#   sumKthSmallestRange: log(N)*log(U)
#   sumLargestK: log(N)*log(U)
#   sumLtX: log(N)*log(U)
#   sumLteX: log(N)*log(U)
#   sumSmallestK: log(N)*log(U)
#   build: N*log(N)*log(U)
# @memory:
#   layout: none
#   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)] S[1*N*log(N)*log(U)]
#   tags: none
#   other: root[1*N] arr[1*N]
#   note: BIT over positions, each BIT node a dynamic value seg tree over [valLo, valHi] (U = its size); nodes are never freed, so each point update adds up to 2 log N log U of them

# a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over positions: BIT node j is a dynamic value
# seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the BIT
# prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
# subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.


class DynamicOrderStats:
    __slots__ = ('arr', 'n', 'vlo', 'vhi', 'root', 'L', 'R', 'C', 'S')

    # O(N log N log U) -- arr: the initial array (a list), 0-indexed; every value a[i] ever holds must lie in
    # [valLo, valHi] (any integers, negative is fine; U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        self.arr = list(arr)
        self.n = len(arr)
        self.vlo, self.vhi = valLo, valHi
        self.root = [0] * (self.n + 1)  # BIT node j's value tree (0: empty)
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
        self.S = [0]
        for i, v in enumerate(arr):
            self._add(i, v, 1)

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.arr[i]

    # O(N) -- the whole array (a copy)
    def getAll(self):
        return list(self.arr)

    # O(logN logU) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        old = self.arr[i]
        if v != old:
            self._add(i, old, -1)
            self._add(i, v, 1)
            self.arr[i] = v

    # O(logN logU) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + v)

    # O(logN logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, max(self.pointGet(i), v))

    # O(logN logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, min(self.pointGet(i), v))

    # O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self.countInValRange(l, r, x, x)

    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else IndexError
    def countInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countInValRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if lowVal > highVal:
            return 0
        return self._countBelow(l, r, highVal + 1) - self._countBelow(l, r, lowVal)

    # O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._countBelow(l, r, x)

    # O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._countBelow(l, r, x + 1)

    # O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return r - l + 1 - self._countBelow(l, r, x + 1)

    # O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return r - l + 1 - self._countBelow(l, r, x)

    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < n and 1 <= k <= r - l + 1, else
    # IndexError
    def kthSmallest(self, l, r, k):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"kthSmallest: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._kth(l, r, 1)

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._kth(l, r, r - l + 1)

    # O(logN) -- smallest value >= x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def smallestGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"smallestGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, x)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def smallestGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"smallestGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, x + 1)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def largestLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"largestLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, x + 1)
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def largestLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"largestLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, x)
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._sumFirst(l, r, r - l + 1)

    # O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else IndexError
    def sumInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumInValRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if lowVal > highVal:
            return 0
        return self._sumBelow(l, r, highVal + 1) - self._sumBelow(l, r, lowVal)

    # O(logN) -- sum of the values < x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def sumLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._sumBelow(l, r, x)

    # O(logN) -- sum of the values <= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def sumLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._sumBelow(l, r, x + 1)

    # O(logN) -- sum of the values > x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def sumGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._sumFirst(l, r, r - l + 1) - self._sumBelow(l, r, x + 1)

    # O(logN) -- sum of the values >= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def sumGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._sumFirst(l, r, r - l + 1) - self._sumBelow(l, r, x)

    # O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= l <= r < n and 0 <= k <= r - l + 1, else
    # IndexError
    def sumSmallestK(self, l, r, k):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumSmallestK: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if not 0 <= k <= r - l + 1:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, k)

    # O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else IndexError; needs
    # 0 <= l <= r < n, else IndexError
    def sumLargestK(self, l, r, k):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumLargestK: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n = r - l + 1
        if not 0 <= k <= n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n) - self._sumFirst(l, r, n - k)

    # O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 0 <= l <= r < n
    # and 1 <= kFrom <= kTo <= r - l + 1, else IndexError
    def sumKthSmallestRange(self, l, r, kFrom, kTo):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumKthSmallestRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if not 1 <= kFrom <= kTo <= r - l + 1:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got "
                             f"kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, kTo) - self._sumFirst(l, r, kFrom - 1)

    # O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest);
    # needs 1 <= kFrom <= kTo <= r - l + 1, else IndexError; needs 0 <= l <= r < n, else IndexError
    def sumKthLargestRange(self, l, r, kFrom, kTo):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumKthLargestRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n = r - l + 1
        if not 1 <= kFrom <= kTo <= n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got "
                             f"kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n - kFrom + 1) - self._sumFirst(l, r, n - kTo)

    # O(logN) -- sum of |a[i] - x| over i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def sumAbsDiffToX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumAbsDiffToX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        rk = x
        c, s = self._countBelow(l, r, rk), self._sumBelow(l, r, rk)
        return x * c - s + (self._sumFirst(l, r, r - l + 1) - s) - x * (r - l + 1 - c)

    # ---- internals ----

    # a[i] = v gains d copies in every BIT node covering i
    def _add(self, i, v, d):
        j = i + 1
        while j <= self.n:
            self.root[j] = self._ins(self.root[j], v, d)
            j += j & -j

    # (trees to add, trees to subtract) for a[l..r]
    def _sides(self, l, r):
        root, pos, neg = self.root, [], []
        j = r + 1
        while j:
            pos.append(root[j])
            j &= j - 1
        j = l
        while j:
            neg.append(root[j])
            j &= j - 1
        return pos, neg

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        return self._kthIn(*self._sides(l, r), k)

    # # of values < x in a[l..r]
    def _countBelow(self, l, r, x):
        if x <= self.vlo:
            return 0
        if x > self.vhi:
            return r - l + 1
        return self._belowIn(*self._sides(l, r), x)[0]

    # sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    def _sumFirst(self, l, r, k):
        return self._sumFirstIn(*self._sides(l, r), k)

    # sum of the values < x in a[l..r]
    def _sumBelow(self, l, r, x):
        if x <= self.vlo:
            return 0
        pos, neg = self._sides(l, r)
        return self._total(pos, neg, self.S) if x > self.vhi else self._belowIn(pos, neg, x)[1]

    # ---- internals: walks over the value trees in pos (added) and neg (subtracted) ----

    def _newNode(self):
        self.L.append(0), self.R.append(0), self.C.append(0), self.S.append(0)
        return len(self.C) - 1

    # tree t (0: a new one) with d more copies of v
    def _ins(self, t, v, d):
        L, R, C, S = self.L, self.R, self.C, self.S
        if not t:
            t = self._newNode()
        top, nl, nh = t, self.vlo, self.vhi
        while True:
            C[t] += d
            S[t] += d * v
            if nl == nh:
                return top
            mid = (nl + nh) >> 1
            if v <= mid:
                if not L[t]:
                    L[t] = self._newNode()
                t, nh = L[t], mid
            else:
                if not R[t]:
                    R[t] = self._newNode()
                t, nl = R[t], mid + 1

    def _total(self, pos, neg, A):
        return sum(A[t] for t in pos) - sum(A[t] for t in neg)

    # the k-th smallest value, 1 <= k <= the trees' count
    def _kthIn(self, pos, neg, k):
        L, R, C = self.L, self.R, self.C
        nl, nh = self.vlo, self.vhi
        while nl != nh:
            mid = (nl + nh) >> 1
            c = sum(C[L[t]] for t in pos) - sum(C[L[t]] for t in neg)
            if k <= c:
                pos, neg, nh = [L[t] for t in pos if L[t]], [L[t] for t in neg if L[t]], mid
            else:
                k -= c
                pos, neg, nl = [R[t] for t in pos if R[t]], [R[t] for t in neg if R[t]], mid + 1
        return nl

    # (# of values < x, their sum), valLo < x <= valHi
    def _belowIn(self, pos, neg, x):
        L, R, C, S = self.L, self.R, self.C, self.S
        nl, nh, cnt, sm = self.vlo, self.vhi, 0, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            if x <= mid:
                pos, neg, nh = [L[t] for t in pos if L[t]], [L[t] for t in neg if L[t]], mid
            else:  # the whole left half is below x
                cnt += sum(C[L[t]] for t in pos) - sum(C[L[t]] for t in neg)
                sm += sum(S[L[t]] for t in pos) - sum(S[L[t]] for t in neg)
                pos, neg, nl = [R[t] for t in pos if R[t]], [R[t] for t in neg if R[t]], mid + 1
        return cnt, sm

    # sum of the k smallest values, 0 <= k <= the trees' count
    def _sumFirstIn(self, pos, neg, k):
        if k <= 0:
            return 0
        L, R, C, S = self.L, self.R, self.C, self.S
        nl, nh, res = self.vlo, self.vhi, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            c = sum(C[L[t]] for t in pos) - sum(C[L[t]] for t in neg)
            if k <= c:
                pos, neg, nh = [L[t] for t in pos if L[t]], [L[t] for t in neg if L[t]], mid
            else:  # the whole left half is among the k smallest
                k -= c
                res += sum(S[L[t]] for t in pos) - sum(S[L[t]] for t in neg)
                pos, neg, nl = [R[t] for t in pos if R[t]], [R[t] for t in neg if R[t]], mid + 1
        return res + k * nl
