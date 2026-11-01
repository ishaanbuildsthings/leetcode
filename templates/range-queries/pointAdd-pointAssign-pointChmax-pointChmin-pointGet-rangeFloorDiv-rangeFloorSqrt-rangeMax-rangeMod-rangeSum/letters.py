# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeFloorDiv-rangeFloorSqrt-rangeMax-rangeMod-rangeSum/letters.py
# @operations: getAll pointAssign pointChmax pointChmin pointGet rangeMax
# @data-structure-type: beats
# @complexities:
#   getAll: N
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeMax: log(N)
#   build: N
# @memory:
#   layout: 4n-recursive
#   node: mx[4*N] tot[4*N]
#   tags: none
#   other: none
#   note: no lazy tags: updates walk down to the leaves that still shrink
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/range-Mod-Sum-FloorDiv-Sqrt-pointAssign.py

# Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
# operations that make sense on characters are listed.

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

    def _pointAssign(self, nodeI, tl, tr, pos, val):
        if tl == tr:
            self.mx[nodeI] = self.tot[nodeI] = val
            return
        tm = (tl + tr) // 2
        if pos <= tm:
            self._pointAssign(2 * nodeI, tl, tm, pos, val)
        else:
            self._pointAssign(2 * nodeI + 1, tm + 1, tr, pos, val)
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
            return ""
        if ql <= tl and qr >= tr:
            return self.mx[nodeI]
        tm = (tl + tr) // 2
        return max(self._rangeMax(2 * nodeI, tl, tm, ql, qr),
                   self._rangeMax(2 * nodeI + 1, tm + 1, tr, ql, qr))

    #################### PUBLIC METHODS START HERE ####################

    # O(log n) -- a[pos] = val. an OVERWRITE, it may RAISE the value
    def pointAssign(self, pos, val):
        self._pointAssign(1, 0, self.n - 1, pos, val)

    # O(logN) -- a[pos]
    def pointGet(self, pos):
        return self._rangeMax(1, 0, self.n - 1, pos, pos)

    def _getAllRec(self, i, tl, tr, out):
        if tl == tr:
            out.append(self.mx[i])
            return
        tm = (tl + tr) // 2
        self._getAllRec(2 * i, tl, tm, out)
        self._getAllRec(2 * i + 1, tm + 1, tr, out)

    # O(N) -- the whole array: one DFS that reads the leaves left to right
    def getAll(self):
        out = []
        if self.n:
            self._getAllRec(1, 0, self.n - 1, out)
        return out

    # O(log n) -- max of l...r
    def rangeMax(self, l, r):
        if l > r or self.n == 0:
            return ""
        return self._rangeMax(1, 0, self.n - 1, l, r)

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)