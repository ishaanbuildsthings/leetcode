# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv rangeFloorSqrt rangeMax rangeMod rangeSum
# @data-structure-type: beats
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeFloorDiv: log(U)*log(U) amortized
#   rangeFloorSqrt: log(U)*log(log(U)) amortized
#   rangeMax: log(U)
#   rangeMod: log(U)*log(U) amortized
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mx[4*log(U)] tot[4*log(U)]
#   tags: none
#   other: none
#   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. C++: one shared node pool, call resetPool() between test cases; Python: per-node lists that grow

# Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
# is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
# right before anything descends past a node or pushes its tags. Otherwise the beats logic below is the
# dense tree's, with children in L / R instead of at 2i / 2i + 1.

# TEMPLATE BY https://github.com/agrawalishaan

# ========================
# COMPLEXITIES

# O(n) build
# seg = SegTree_PERFORMANT(arr)

# C = largest value in the array
# O(logN):              pointAssign(pos, newVal)
# O(logN * logC):       rangeMod(l, r, mod)
# O(logN * logC):       rangeFloorDiv(l, r, div) floor divide each element
# O(logN * log(logC)):  rangeFloorSqrt(l, r) floor sqrt each element

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


class SparseSegTree:
    __slots__ = ("lo", "hi", "L", "R", "ln", "mx", "tot")

    # O(n)
    # O(1) -- all zeros over [lo, hi]; any range of integers works
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        # node 0 is unused; node 1 is the root, one block of hi - lo + 1 zeros
        self.L, self.R, self.ln = [0, 0], [0, 0], [0, 0]
        self.mx = [0] * 2
        self.tot = [0] * 2
        self._zero(1, hi - lo + 1)

    # node i becomes a block of k zeros (its defaults, plus every count = k)
    def _zero(self, i, k):
        self.ln[i] = k

    # a fresh node: a block of k zeros
    def _node(self, k):
        j = len(self.L)
        self.L.append(0)
        self.R.append(0)
        self.ln.append(0)
        self.mx.append(0)
        self.tot.append(0)
        self._zero(j, k)
        return j

    # create node i's children (blocks of zeros: the left one gets the extra slot) if it has none yet
    def _kids(self, i):
        if not self.L[i] and self.ln[i] > 1:
            k = self.ln[i]
            self.L[i] = self._node((k + 1) // 2)
            self.R[i] = self._node(k // 2)

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
        self._kids(nodeI)
        tm = (tl + tr) // 2
        self._rangeShrink(self.L[nodeI], tl, tm, ql, qr, cutoff, leafOp)
        self._rangeShrink(self.R[nodeI], tm + 1, tr, ql, qr, cutoff, leafOp)
        left, right = self.L[nodeI], self.R[nodeI]
        self.mx[nodeI] = self.mx[left] if self.mx[left] > self.mx[right] else self.mx[right]
        self.tot[nodeI] = self.tot[left] + self.tot[right]

    def _pointAssign(self, nodeI, tl, tr, pos, val):
        if tl == tr:
            self.mx[nodeI] = self.tot[nodeI] = val
            return
        self._kids(nodeI)
        tm = (tl + tr) // 2
        if pos <= tm:
            self._pointAssign(self.L[nodeI], tl, tm, pos, val)
        else:
            self._pointAssign(self.R[nodeI], tm + 1, tr, pos, val)
        left, right = self.L[nodeI], self.R[nodeI]
        self.mx[nodeI] = self.mx[left] if self.mx[left] > self.mx[right] else self.mx[right]
        self.tot[nodeI] = self.tot[left] + self.tot[right]

    def _rangeSum(self, nodeI, tl, tr, ql, qr):
        if ql > tr or qr < tl:
            return 0
        if ql <= tl and qr >= tr:
            return self.tot[nodeI]
        self._kids(nodeI)
        tm = (tl + tr) // 2
        return (self._rangeSum(self.L[nodeI], tl, tm, ql, qr)
                + self._rangeSum(self.R[nodeI], tm + 1, tr, ql, qr))

    def _rangeMax(self, nodeI, tl, tr, ql, qr):
        if ql > tr or qr < tl:
            return float("-inf")
        if ql <= tl and qr >= tr:
            return self.mx[nodeI]
        self._kids(nodeI)
        tm = (tl + tr) // 2
        return max(self._rangeMax(self.L[nodeI], tl, tm, ql, qr),
                   self._rangeMax(self.R[nodeI], tm + 1, tr, ql, qr))

    #################### PUBLIC METHODS START HERE ####################

    # amortized O(log n * log C) -- a[i] %= x for every i in l...r
    # prune at mx < x: everything there is already below x, so a % x == a
    def rangeMod(self, l, r, x):
        if l > r:
            return
        self._rangeShrink(1, self.lo, self.hi, l, r, x, lambda val: val % x)

    # amortized O(log n * log C) -- a[i] //= x for every i in l...r. requires x >= 2
    # prune at mx < 1: only zeros left, and 0 // x == 0
    def rangeFloorDiv(self, l, r, x):
        if l > r or x < 2:
            return
        self._rangeShrink(1, self.lo, self.hi, l, r, 1, lambda val: val // x)

    # amortized O(log n * log log C) -- a[i] = floor(sqrt(a[i])) for every i in l...r
    # prune at mx < 2: 0 and 1 are fixed points
    def rangeFloorSqrt(self, l, r):
        if l > r:
            return
        self._rangeShrink(1, self.lo, self.hi, l, r, 2, isqrt)

    # O(log n) -- a[pos] = val. an OVERWRITE, it may RAISE the value
    def pointAssign(self, pos, val):
        self._pointAssign(1, self.lo, self.hi, pos, val)

    # O(log n)
    def pointGet(self, pos):
        return self._rangeMax(1, self.lo, self.hi, pos, pos)

    # O(log n) -- sum of l...r
    def rangeSum(self, l, r):
        if l > r:
            return 0
        return self._rangeSum(1, self.lo, self.hi, l, r)

    # O(log n) -- max of l...r
    def rangeMax(self, l, r):
        if l > r:
            return float("-inf")
        return self._rangeMax(1, self.lo, self.hi, l, r)

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)