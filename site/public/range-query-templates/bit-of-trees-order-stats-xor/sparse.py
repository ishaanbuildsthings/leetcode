# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/bit-of-trees-order-stats-xor/sparse.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin smallestGtX smallestGteX xorGtX xorGteX xorInValRange xorLtX xorLteX
# @data-structure-type: bit-of-trees
# @complexities:
#   countGtX: log(U)*log(U)
#   countGteX: log(U)*log(U)
#   countInValRange: log(U)*log(U)
#   countLtX: log(U)*log(U)
#   countLteX: log(U)*log(U)
#   countOccurrences: log(U)*log(U)
#   kthSmallest: log(U)*log(U)
#   largestLtX: log(U)*log(U)
#   largestLteX: log(U)*log(U)
#   pointAdd: log(U)*log(U)
#   pointAssign: log(U)*log(U)
#   pointChmax: log(U)*log(U)
#   pointChmin: log(U)*log(U)
#   pointGet: 1
#   rangeMax: log(U)*log(U)
#   rangeMin: log(U)*log(U)
#   smallestGtX: log(U)*log(U)
#   smallestGteX: log(U)*log(U)
#   xorGtX: log(U)*log(U)
#   xorGteX: log(U)*log(U)
#   xorInValRange: log(U)*log(U)
#   xorLtX: log(U)*log(U)
#   xorLteX: log(U)*log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: L[1*log(U)*log(U)] R[1*log(U)*log(U)] C[1*log(U)*log(U)] X[1*log(U)*log(U)]
#   tags: none
#   other: root[1*log(U)] vals[1]
#   note: any index range [lo, hi], every position starting at 0; only nonzero values are stored, and the zeros of [l, r] are counted in closed form; U = the larger of the index range and the value range [valLo, valHi]; sizes are per point update

# a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over the index range [lo, hi]: BIT node j is a
# dynamic value
# seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the BIT
# prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
# subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.
# Sparse: every position of [lo, hi] starts at 0 and only nonzero values are stored; the zeros of [l, r] (its length
# minus the stored values in it) sit between the stored negatives and positives.


from random import getrandbits

SALT = getrandbits(62)  # dict keys are salted positions, so no fixed input can make the dict collide


class SparseDynamicOrderStats:
    __slots__ = ('lo', 'hi', 'vals', 'vlo', 'vhi', 'root', 'L', 'R', 'C', 'X')

    # O(1) -- indices: any integers in [lo, hi], every position starting at 0; every value a[i] ever holds must lie in
    # [valLo, valHi] (U = the larger of the two ranges' sizes)
    def __init__(self, lo, hi, valLo, valHi):
        self.lo, self.hi = lo, hi
        self.vlo, self.vhi = valLo, valHi
        self.vals = {}  # nonzero values only
        self.root = {}  # BIT node -> its value tree (missing: empty)
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
        self.X = [0]  # xor of the values below with an odd count

    # O(1) -- a[i]; needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointGet: needs lo <= i <= hi, got i = {i}")
        return self.vals.get(i ^ SALT, 0)

    # O(logU * logU) -- a[i] = v; needs lo <= i <= hi, else IndexError
    def pointAssign(self, i, v):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAssign: needs lo <= i <= hi, got i = {i}")
        old = self.vals.get(i ^ SALT, 0)
        if v != old:
            if old:
                self._add(i, old, -1)
            if v:
                self._add(i, v, 1)
                self.vals[i ^ SALT] = v
            else:
                self.vals.pop(i ^ SALT, None)

    # O(logU * logU) -- a[i] += v; needs lo <= i <= hi, else IndexError
    def pointAdd(self, i, v):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAdd: needs lo <= i <= hi, got i = {i}")
        self.pointAssign(i, self.pointGet(i) + v)

    # O(logU * logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else IndexError
    def pointChmax(self, i, v):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmax: needs lo <= i <= hi, got i = {i}")
        self.pointAssign(i, max(self.pointGet(i), v))

    # O(logU * logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else IndexError
    def pointChmin(self, i, v):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmin: needs lo <= i <= hi, got i = {i}")
        self.pointAssign(i, min(self.pointGet(i), v))

    # O(logU * logU) -- # of i in [l, r] with a[i] == x; needs lo <= l <= r <= hi, else IndexError
    def countOccurrences(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countOccurrences: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self.countInValRange(l, r, x, x)

    # O(logU * logU) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs lo <= l <= r <= hi, else IndexError
    def countInValRange(self, l, r, lowVal, highVal):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countInValRange: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if lowVal > highVal:
            return 0
        return self._countBelow(l, r, highVal + 1) - self._countBelow(l, r, lowVal)

    # O(logU * logU) -- # of values < x in a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def countLtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self._countBelow(l, r, x)

    # O(logU * logU) -- # of values <= x in a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def countLteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self._countBelow(l, r, x + 1)

    # O(logU * logU) -- # of values > x in a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def countGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return r - l + 1 - self._countBelow(l, r, x + 1)

    # O(logU * logU) -- # of values >= x in a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def countGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return r - l + 1 - self._countBelow(l, r, x)

    # O(logU * logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs lo <= l <= r <= hi and 1 <= k <= r - l +
    # 1,
    # else IndexError
    def kthSmallest(self, l, r, k):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"kthSmallest: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logU * logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMin(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeMin: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self._kth(l, r, 1)

    # O(logU * logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMax(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeMax: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self._kth(l, r, r - l + 1)

    # O(logU * logU) -- smallest value >= x in a[l..r], or None; needs lo <= l <= r <= hi, else IndexError
    def smallestGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"smallestGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        c = self._countBelow(l, r, x)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logU * logU) -- smallest value > x in a[l..r], or None; needs lo <= l <= r <= hi, else IndexError
    def smallestGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"smallestGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        c = self._countBelow(l, r, x + 1)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logU * logU) -- largest value <= x in a[l..r], or None; needs lo <= l <= r <= hi, else IndexError
    def largestLteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"largestLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        c = self._countBelow(l, r, x + 1)
        return None if c == 0 else self._kth(l, r, c)

    # O(logU * logU) -- largest value < x in a[l..r], or None; needs lo <= l <= r <= hi, else IndexError
    def largestLtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"largestLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        c = self._countBelow(l, r, x)
        return None if c == 0 else self._kth(l, r, c)

    # ---- internals ----

    # a[i] = v gains d copies in every BIT node covering i
    def _add(self, i, v, d):
        j, m = i - self.lo + 1, self.hi - self.lo + 1
        while j <= m:
            self.root[j ^ SALT] = self._ins(self.root.get(j ^ SALT, 0), v, d)
            j += j & -j

    # (trees to add, trees to subtract, zeros in a[l..r])
    def _sides(self, l, r):
        root, pos, neg = self.root, [], []
        j = r - self.lo + 1
        while j:
            pos.append(root.get(j ^ SALT, 0))
            j &= j - 1
        j = l - self.lo
        while j:
            neg.append(root.get(j ^ SALT, 0))
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

    # O(logU * logU) -- xor of the values < x in a[l..r] (copies count); 0 if there are none; needs lo <= l <= r <= hi,
    # else IndexError
    def xorLtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"xorLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self._xorBelow(l, r, x)

    # O(logU * logU) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none; needs lo <= l <= r <= hi,
    # else IndexError
    def xorLteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"xorLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self._xorBelow(l, r, x + 1)

    # O(logU * logU) -- xor of the values > x in a[l..r] (copies count); 0 if there are none; needs lo <= l <= r <= hi,
    # else IndexError
    def xorGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"xorGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self._xorBelow(l, r, self.vhi + 1) ^ self._xorBelow(l, r, x + 1)

    # O(logU * logU) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none; needs lo <= l <= r <= hi,
    # else IndexError
    def xorGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"xorGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self._xorBelow(l, r, self.vhi + 1) ^ self._xorBelow(l, r, x)

    # O(logU * logU) -- xor of the a[i] in [l, r] with lowVal <= a[i] <= highVal (copies count); 0 if there are none;
    # needs lo <= l <= r <= hi, else IndexError
    def xorInValRange(self, l, r, lowVal, highVal):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"xorInValRange: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if lowVal > highVal:
            return 0
        return self._xorBelow(l, r, highVal + 1) ^ self._xorBelow(l, r, lowVal)

    # xor of the values < x in a[l..r] (the zeros add nothing)
    def _xorBelow(self, l, r, x):
        if x <= self.vlo:
            return 0
        pos, neg = self._sides(l, r)[:2]
        L, R, X, res = self.L, self.R, self.X, 0
        if x > self.vhi:
            for t in pos + neg:
                res ^= X[t]
            return res
        nl, nh = self.vlo, self.vhi
        while nl != nh:
            mid = (nl + nh) >> 1
            if x <= mid:
                pos, neg, nh = [L[t] for t in pos if L[t]], [L[t] for t in neg if L[t]], mid
            else:  # the whole left half is below x
                for t in pos + neg:
                    res ^= X[L[t]]
                pos, neg, nl = [R[t] for t in pos if R[t]], [R[t] for t in neg if R[t]], mid + 1
        return res

    # ---- internals: walks over the value trees in pos (added) and neg (subtracted) ----

    def _newNode(self):
        self.L.append(0), self.R.append(0), self.C.append(0), self.X.append(0)
        return len(self.C) - 1

    # tree t (0: a new one) with d more copies of v
    def _ins(self, t, v, d):
        L, R, C = self.L, self.R, self.C
        if not t:
            t = self._newNode()
        top, nl, nh = t, self.vlo, self.vhi
        while True:
            C[t] += d
            if d & 1:
                self.X[t] ^= v
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
