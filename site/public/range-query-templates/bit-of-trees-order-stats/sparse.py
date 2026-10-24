# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/bit-of-trees-order-stats/sparse.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin smallestGtX smallestGteX
# @data-structure-type: bit-of-trees
# @complexities:
#   countGtX: log(U)*log(U)
#   countGteX: log(U)*log(U)
#   countInValRange: log(U)*log(U)
#   countLtX: log(U)*log(U)
#   countLteX: log(U)*log(U)
#   countOccurrences: log(U)*log(U)
#   kthLargest: log(U)*log(U)
#   kthSmallest: log(U)*log(U)
#   largestLtX: log(U)*log(U)
#   largestLteX: log(U)*log(U)
#   medianHigh: log(U)*log(U)
#   medianLow: log(U)*log(U)
#   pointAdd: log(U)*log(U)
#   pointAssign: log(U)*log(U)
#   pointChmax: log(U)*log(U)
#   pointChmin: log(U)*log(U)
#   pointGet: 1
#   rangeMax: log(U)*log(U)
#   rangeMin: log(U)*log(U)
#   smallestGtX: log(U)*log(U)
#   smallestGteX: log(U)*log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: L[1*log(U)*log(U)] R[1*log(U)*log(U)] C[1*log(U)*log(U)]
#   tags: none
#   other: root[1*log(U)] vals[1]
#   note: any index range [lo, hi], every position starting at 0; only nonzero values are stored, and the zeros of [l, r] are counted in closed form; U = the larger of the index range and the value range [valLo, valHi]; sizes are per point update

# a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over the index range [lo, hi]: BIT node j is a dynamic value
# seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the BIT
# prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
# subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.
# Sparse: every position of [lo, hi] starts at 0 and only nonzero values are stored; the zeros of [l, r] (its length
# minus the stored values in it) sit between the stored negatives and positives.


class SparseDynamicOrderStats:
    __slots__ = ('lo', 'hi', 'vals', 'vlo', 'vhi', 'root', 'L', 'R', 'C')

    # O(1) -- indices: any integers in [lo, hi], every position starting at 0; every value a[i] ever holds must lie in
    # [valLo, valHi] (U = the larger of the two ranges' sizes)
    def __init__(self, lo, hi, valLo, valHi):
        self.lo, self.hi = lo, hi
        self.vlo, self.vhi = valLo, valHi
        self.vals = {}  # nonzero values only
        self.root = {}  # BIT node -> its value tree (missing: empty)
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.vals.get(i, 0)

    # O(logN logU) -- a[i] = v
    def pointAssign(self, i, v):
        old = self.vals.get(i, 0)
        if v != old:
            if old:
                self._add(i, old, -1)
            if v:
                self._add(i, v, 1)
                self.vals[i] = v
            else:
                self.vals.pop(i, None)

    # O(logN logU) -- a[i] += v
    def pointAdd(self, i, v):
        self.pointAssign(i, self.pointGet(i) + v)

    # O(logN logU) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        self.pointAssign(i, max(self.pointGet(i), v))

    # O(logN logU) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        self.pointAssign(i, min(self.pointGet(i), v))

    # O(logN) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        return self.countInValRange(l, r, x, x)

    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    def countInValRange(self, l, r, lowVal, highVal):
        if lowVal > highVal:
            return 0
        return self._countBelow(l, r, highVal + 1) - self._countBelow(l, r, lowVal)

    # O(logN) -- # of values < x in a[l..r]
    def countLtX(self, l, r, x):
        return self._countBelow(l, r, x)

    # O(logN) -- # of values <= x in a[l..r]
    def countLteX(self, l, r, x):
        return self._countBelow(l, r, x + 1)

    # O(logN) -- # of values > x in a[l..r]
    def countGtX(self, l, r, x):
        return r - l + 1 - self._countBelow(l, r, x + 1)

    # O(logN) -- # of values >= x in a[l..r]
    def countGteX(self, l, r, x):
        return r - l + 1 - self._countBelow(l, r, x)

    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else IndexError
    def kthSmallest(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else IndexError
    def kthLargest(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthLargest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, r - l + 2 - k)

    # O(logN) -- lower median of a[l..r]: its ceil(len / 2)-th smallest
    def medianLow(self, l, r):
        return self._kth(l, r, (r - l + 2) // 2)

    # O(logN) -- upper median of a[l..r]: its (floor(len / 2) + 1)-th smallest
    def medianHigh(self, l, r):
        return self._kth(l, r, (r - l + 1) // 2 + 1)

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        return self._kth(l, r, 1)

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        return self._kth(l, r, r - l + 1)

    # O(logN) -- smallest value >= x in a[l..r], or None
    def smallestGteX(self, l, r, x):
        c = self._countBelow(l, r, x)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- smallest value > x in a[l..r], or None
    def smallestGtX(self, l, r, x):
        c = self._countBelow(l, r, x + 1)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- largest value <= x in a[l..r], or None
    def largestLteX(self, l, r, x):
        c = self._countBelow(l, r, x + 1)
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- largest value < x in a[l..r], or None
    def largestLtX(self, l, r, x):
        c = self._countBelow(l, r, x)
        return None if c == 0 else self._kth(l, r, c)

    # ---- internals ----

    # a[i] = v gains d copies in every BIT node covering i
    def _add(self, i, v, d):
        j, m = i - self.lo + 1, self.hi - self.lo + 1
        while j <= m:
            self.root[j] = self._ins(self.root.get(j, 0), v, d)
            j += j & -j

    # (trees to add, trees to subtract, zeros in a[l..r])
    def _sides(self, l, r):
        root, pos, neg = self.root, [], []
        j = r - self.lo + 1
        while j:
            pos.append(root.get(j, 0))
            j &= j - 1
        j = l - self.lo
        while j:
            neg.append(root.get(j, 0))
            j &= j - 1
        return pos, neg, (r - l + 1) - self._total(pos, neg, self.C)

    # # of stored (nonzero) values < x
    def _storedBelow(self, pos, neg, x):
        if x <= self.vlo:
            return 0
        if x > self.vhi:
            return self._total(pos, neg, self.C)
        return self._belowIn(pos, neg, x)[0]

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        pos, neg, zeros = self._sides(l, r)
        negs = self._storedBelow(pos, neg, 0)
        if k <= negs:
            return self._kthIn(pos, neg, k)
        if k <= negs + zeros:
            return 0
        return self._kthIn(pos, neg, k - zeros)

    # # of values < x in a[l..r]
    def _countBelow(self, l, r, x):
        pos, neg, zeros = self._sides(l, r)
        return self._storedBelow(pos, neg, x) + (zeros if 0 < x else 0)

    # ---- internals: walks over the value trees in pos (added) and neg (subtracted) ----

    def _newNode(self):
        self.L.append(0), self.R.append(0), self.C.append(0)
        return len(self.C) - 1

    # tree t (0: a new one) with d more copies of v
    def _ins(self, t, v, d):
        L, R, C = self.L, self.R, self.C
        if not t:
            t = self._newNode()
        top, nl, nh = t, self.vlo, self.vhi
        while True:
            C[t] += d
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
        L, R, C = self.L, self.R, self.C
        nl, nh, cnt, sm = self.vlo, self.vhi, 0, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            if x <= mid:
                pos, neg, nh = [L[t] for t in pos if L[t]], [L[t] for t in neg if L[t]], mid
            else:  # the whole left half is below x
                cnt += sum(C[L[t]] for t in pos) - sum(C[L[t]] for t in neg)
                pos, neg, nl = [R[t] for t in pos if R[t]], [R[t] for t in neg if R[t]], mid + 1
        return cnt, sm
