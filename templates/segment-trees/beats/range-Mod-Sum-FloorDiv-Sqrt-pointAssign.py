# TEMPLATE BY https://github.com/agrawalishaan

# ========================
# COMPLEXITIES

# O(n) build
# seg = SegTree_PERFORMANT(arr)

# C = largest value in the array
# O(logN):              pointSet(pos, newVal)
# O(logN * logC):       rangeMod(l, r, mod)
# O(logN * logC):       rangeDiv(l, r, div) floor divide each element
# O(logN * log(logC)):  rangeSqrt(l, r) floor sqrt each element

# O(logN):              rangeSum(l, r)


# ========================
"""
HOW DO POTENTIALS WORK? (rangeMod example)

First when we do A%B with A>=B, A always falls by at least half. If B is < half of A, then obviously A is halved. If it is bigger, it is obviously halved too.

Think about the "potential" of the entire segment tree. There are N values in logN layers, so N log N values are captured across all segment tree nodes.
Each value can be halved at most logC times, so the potential across the whole tree is N logN log C.


There are 3 types of nodes in a seg tree:

1) STRADDLES THE QUERY RANGE (always recurses)
at most 2*logN visited per query

2) DEAD-END NODE (does not recurse)
always comes from one of the other nodes so these are free

3) FULLY COVERED NODES THAT DO RECURSE
in a normal segment tree we stop as soon as we hit one, here we do not
We must show the # of fully covered nodes we visit is bounded, as the others are bounded, then our total visits is bounded

When we visit a fully covered node and the max is < our mod, we terminate immediately (this falls into case 2)
If it is not, there is at least one value in this range that is going to halve, dropping the potential of our entire tree. We recurse to the children.

So at most we visit O(N logN logC) nodes in our rangeMod.

POINT SET:
This increases the potential of a logN nodes by logC each, so across Q point sets we increase potential by Q logN logC.

"""

# ========================


from math import isqrt


class SegTree_PERFORMANT:
    __slots__ = ("n", "mx", "tot")

    # O(n)
    def __init__(self, arr):
        self.n = len(arr)
        size = 4 * max(1, self.n)
        self.mx = [0] * size
        self.tot = [0] * size
        if self.n:
            self._build(1, 0, self.n - 1, arr)

    def _build(self, nodeI, tl, tr, arr):
        if tl == tr:
            self.mx[nodeI] = self.tot[nodeI] = arr[tl]
            return
        tm = (tl + tr) // 2
        self._build(2 * nodeI, tl, tm, arr)
        self._build(2 * nodeI + 1, tm + 1, tr, arr)
        left, right = 2 * nodeI, 2 * nodeI + 1
        self.mx[nodeI] = self.mx[left] if self.mx[left] > self.mx[right] else self.mx[right]
        self.tot[nodeI] = self.tot[left] + self.tot[right]

    # shared driver: descend to leaves, pruning any subtree whose max says nothing can change.
    # leafOp maps one value to its new value, cutoff is the max below which nothing changes.
    def _rangeShrink(self, nodeI, tl, tr, ql, qr, cutoff, leafOp):
        # oob
        if qr < tl or ql > tr:
            return
        # nothing under here can change
        if self.mx[nodeI] < cutoff:
            return
        # leaf, this is where the op actually happens
        if tl == tr:
            self.mx[nodeI] = self.tot[nodeI] = leafOp(self.mx[nodeI])
            return
        tm = (tl + tr) // 2
        self._rangeShrink(2 * nodeI, tl, tm, ql, qr, cutoff, leafOp)
        self._rangeShrink(2 * nodeI + 1, tm + 1, tr, ql, qr, cutoff, leafOp)
        left, right = 2 * nodeI, 2 * nodeI + 1
        self.mx[nodeI] = self.mx[left] if self.mx[left] > self.mx[right] else self.mx[right]
        self.tot[nodeI] = self.tot[left] + self.tot[right]

    def _pointSet(self, nodeI, tl, tr, pos, val):
        if tl == tr:
            self.mx[nodeI] = self.tot[nodeI] = val
            return
        tm = (tl + tr) // 2
        if pos <= tm:
            self._pointSet(2 * nodeI, tl, tm, pos, val)
        else:
            self._pointSet(2 * nodeI + 1, tm + 1, tr, pos, val)
        left, right = 2 * nodeI, 2 * nodeI + 1
        self.mx[nodeI] = self.mx[left] if self.mx[left] > self.mx[right] else self.mx[right]
        self.tot[nodeI] = self.tot[left] + self.tot[right]

    def _rangeSum(self, nodeI, tl, tr, ql, qr):
        if ql > tr or qr < tl:
            return 0
        if ql <= tl and qr >= tr:
            return self.tot[nodeI]
        tm = (tl + tr) // 2
        return (self._rangeSum(2 * nodeI, tl, tm, ql, qr)
                + self._rangeSum(2 * nodeI + 1, tm + 1, tr, ql, qr))

    def _rangeMax(self, nodeI, tl, tr, ql, qr):
        if ql > tr or qr < tl:
            return float("-inf")
        if ql <= tl and qr >= tr:
            return self.mx[nodeI]
        tm = (tl + tr) // 2
        return max(self._rangeMax(2 * nodeI, tl, tm, ql, qr),
                   self._rangeMax(2 * nodeI + 1, tm + 1, tr, ql, qr))

    #################### PUBLIC METHODS START HERE ####################

    # amortized O(log n * log C) -- a[i] %= x for every i in l...r
    # prune at mx < x: everything there is already below x, so a % x == a
    def rangeMod(self, l, r, x):
        if l > r or self.n == 0:
            return
        self._rangeShrink(1, 0, self.n - 1, l, r, x, lambda val: val % x)

    # amortized O(log n * log C) -- a[i] //= x for every i in l...r. requires x >= 2
    # prune at mx < 1: only zeros left, and 0 // x == 0
    def rangeDiv(self, l, r, x):
        if l > r or self.n == 0 or x < 2:
            return
        self._rangeShrink(1, 0, self.n - 1, l, r, 1, lambda val: val // x)

    # amortized O(log n * log log C) -- a[i] = floor(sqrt(a[i])) for every i in l...r
    # prune at mx < 2: 0 and 1 are fixed points
    def rangeSqrt(self, l, r):
        if l > r or self.n == 0:
            return
        self._rangeShrink(1, 0, self.n - 1, l, r, 2, isqrt)

    # O(log n) -- a[pos] = val. an OVERWRITE, it may RAISE the value
    def pointSet(self, pos, val):
        self._pointSet(1, 0, self.n - 1, pos, val)

    # O(log n)
    def pointGet(self, pos):
        return self._rangeMax(1, 0, self.n - 1, pos, pos)

    # O(log n) -- sum of l...r
    def rangeSum(self, l, r):
        if l > r or self.n == 0:
            return 0
        return self._rangeSum(1, 0, self.n - 1, l, r)

    # O(log n) -- max of l...r
    def rangeMax(self, l, r):
        if l > r or self.n == 0:
            return float("-inf")
        return self._rangeMax(1, 0, self.n - 1, l, r)