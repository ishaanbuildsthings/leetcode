# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAffineMod rangeAssign rangeMultMod rangeSum
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeAffineMod: log(N)
#   rangeAssign: log(N)
#   rangeMultMod: log(N)
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: pow2-iterative
#   node: tot[4*N]
#   tags: mult[2*N] add[2*N]
#   other: none
#   note: one affine tag (mult, add) per node: x -> x*mult + add (mod p)
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/lazy/Range-Add-Assign-Sum-MultFixedMod-AffineFixedMod-PointSet.py

# TEMPLATE BY https://github.com/agrawalishaan
#
# ========================
# COMPLEXITIES
#
# O(n) build
# seg = AffineSeg_PERFORMANT(arr)
#
# O(logN):  rangeAdd(l, r, x)         -- a[i] += x
# O(logN):  rangeMultMod(l, r, m)        -- a[i] *= m
# O(logN):  rangeAssign(l, r, x)      -- a[i] = x
# O(logN):  rangeAffineMod(l, r, m, x)   -- a[i] = a[i]*m + x, the general one
# O(logN):  pointAssign(pos, newVal)     -- OVERWRITE
# O(logN):  rangeSum(l, r)
# O(logN):  pointGet(pos)
# O(n) space
#
# NOT amortized, plain lazy propagation, worst case logN per op. Everything is mod self.mod
# (1e9+7 by default, change the constant). Negative inputs are normalized on the way in.
#
# ========================
#
"""
WHY ONE (mult, add) PAIR IS ENOUGH

Every one of these updates is an AFFINE map v -> v*m + x, and affine maps compose into affine
maps, so a whole history of them collapses into two numbers. Applying f(v) = m1*v + a1 and THEN
g(v) = m2*v + a2:

    g(f(v)) = m2*(m1*v + a1) + a2 = (m1*m2)*v + (a1*m2 + a2)

so  newMult = m1*m2  and  newAdd = a1*m2 + a2.

THE ONLY LINE THAT IS EASY TO GET WRONG IS THAT SECOND ONE. The OLD add has to be scaled by the
NEW mult. Writing newAdd = a1 + a2 looks right and passes small tests where no multiply has
landed yet, then silently gives wrong answers the moment one has.

MULTIPLY-BEFORE-ADD IS THE FORM THAT CLOSES, and that is not arbitrary. Keep the other form,
(v + b)*m, and a later add d needs (v + b)*m + d -- there is no b' making (v + b')*m equal that
without dividing. Multiply-first survives both operations, so that is the canonical form.

Every update is a special case, which is why there is only one tag type and one apply function:
    add x     -> (m, a) = (1, x)
    mult m    -> (m, a) = (m, 0)
    assign x  -> (m, a) = (0, x)      multiply by zero, then add -- no separate assign tag
Note that assign being free depends on working mod a prime; without the mod you would still be
fine here since 0 is a legal multiplier, but the inverse does not exist, so nothing that needs to
UNDO a tag would work.

SUM SURVIVES, MIN AND MAX DO NOT. A node's sum transforms as tot*m + a*width, which needs only
the width. min and max are hopeless under multiply because the mod wraps, so ordering is
destroyed -- do not add them to this file.

Pending tags have to be pushed off the two boundary root-to-leaf paths before an update or a query touches
anything below them, or the order of tags gets scrambled (affine maps do not commute). pointAssign is just
rangeAffineMod(i, i, 0, v), so it goes through the same push and needs no special case.
"""

# ========================



class AffineSeg_PERFORMANT:
    """Iterative lazy tree over a power-of-two layout. An update pushes every tag on its two boundary
    root-to-leaf paths, tags the O(log N) covering nodes, then recomputes the boundary paths bottom-up."""
    __slots__ = ("n", "mod", "size", "H", "tot", "mult", "add")

    # O(N)
    def __init__(self, arr, mod=1000000007):
        self.mod = mod
        n = self.n = len(arr)
        size, H = 1, 0
        while size < max(n, 1):
            size <<= 1
            H += 1
        self.size, self.H = size, H
        tot = self.tot = [0] * (2 * size)
        for i, v in enumerate(arr):
            tot[size + i] = v % mod
        for x in range(size - 1, 0, -1):
            tot[x] = (tot[2 * x] + tot[2 * x + 1]) % mod
        self.mult = [1] * size  # tags live on internal nodes only
        self.add = [0] * size

    # v -> v*m + a on every slot of node x, which covers `length` slots. Composition is (m1*m2, a1*m2 + a2):
    # the OLD add has to be scaled by the NEW mult, which is the step people drop.
    def _apply(self, x, length, m, a):
        mod = self.mod
        self.tot[x] = (self.tot[x] * m + a * length) % mod
        if x < self.size:
            self.mult[x] = self.mult[x] * m % mod
            self.add[x] = (self.add[x] * m + a) % mod

    def _push(self, x, childLen):
        m, a = self.mult[x], self.add[x]
        if m != 1 or a:
            self._apply(2 * x, childLen, m, a)
            self._apply(2 * x + 1, childLen, m, a)
            self.mult[x] = 1
            self.add[x] = 0

    def _pushToRoot(self, p):
        for s in range(self.H, 0, -1):
            self._push(p >> s, 1 << (s - 1))

    # a node tagged during this update keeps its own tag's effect on top of its children
    def _recomputeToRoot(self, p):
        tot, mult, add, mod = self.tot, self.mult, self.add, self.mod
        p >>= 1
        length = 2
        while p:
            tot[p] = ((tot[2 * p] + tot[2 * p + 1]) * mult[p] + add[p] * length) % mod
            p >>= 1
            length <<= 1

    ################ PUBLIC METHODS START HERE ################

    # O(log n) -- a[i] = a[i]*m + x for every i in l...r. every other update is this one
    def rangeAffineMod(self, l, r, m, x):
        if l > r:
            return
        mod = self.mod
        m %= mod
        x %= mod
        l0, r0 = l + self.size, r + self.size
        self._pushToRoot(l0)
        self._pushToRoot(r0)
        lo, hi, length = l0, r0 + 1, 1
        while lo < hi:
            if lo & 1:
                self._apply(lo, length, m, x)
                lo += 1
            if hi & 1:
                hi -= 1
                self._apply(hi, length, m, x)
            lo >>= 1
            hi >>= 1
            length <<= 1
        self._recomputeToRoot(l0)
        self._recomputeToRoot(r0)

    # O(log n) -- a[i] += x
    def rangeAdd(self, l, r, x):
        self.rangeAffineMod(l, r, 1, x)

    # O(log n) -- a[i] *= m
    def rangeMultMod(self, l, r, m):
        self.rangeAffineMod(l, r, m, 0)

    # O(log n) -- a[i] = x. multiplying by 0 then adding x, no separate tag needed
    def rangeAssign(self, l, r, x):
        self.rangeAffineMod(l, r, 0, x)

    # O(log n) -- sum of l...r, mod p
    def rangeSum(self, l, r):
        if l > r:
            return 0
        l += self.size
        r += self.size
        self._pushToRoot(l)
        self._pushToRoot(r)
        tot = self.tot
        res = 0
        r += 1
        while l < r:
            if l & 1:
                res += tot[l]
                l += 1
            if r & 1:
                r -= 1
                res += tot[r]
            l >>= 1
            r >>= 1
        return res % self.mod

    # O(log n) -- a[i] = v
    def pointAssign(self, i, v):
        self.rangeAffineMod(i, i, 0, v)

    # O(log n) -- a[i], in [0, mod)
    def pointGet(self, i):
        p = i + self.size
        self._pushToRoot(p)
        return self.tot[p]

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
        self.rangeAdd(i, i, delta)
