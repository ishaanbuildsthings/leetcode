# TEMPLATE BY https://github.com/agrawalishaan
#
# ========================
# COMPLEXITIES
#
# O(n) build
# seg = AffineSeg_PERFORMANT(arr)
#
# O(logN):  rangeAdd(l, r, x)         -- a[i] += x
# O(logN):  rangeMult(l, r, m)        -- a[i] *= m
# O(logN):  rangeAssign(l, r, x)      -- a[i] = x
# O(logN):  rangeAffine(l, r, m, x)   -- a[i] = a[i]*m + x, the general one
# O(logN):  pointSet(pos, newVal)     -- OVERWRITE
# O(logN):  rangeSum(l, r)
# O(logN):  pointGet(pos)
# O(n) space
#
# NOT amortized, plain lazy propagation, worst case logN per op. Everything is mod MOD
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

_push has to run before ANY descent, including in rangeSum and pointSet, or pending tags never
reach the leaves. pointSet also has to reset the leaf's own tag, otherwise the slot inherits
every operation that happened before it was written.
"""

# ========================


MOD = 1000000007


class AffineSeg_PERFORMANT:
    def __init__(self, arr):
        self.n = n = len(arr)
        size = 4 * max(1, n)
        self.tot = [0] * size
        self.mult = [1] * size
        self.add = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        self.mult[i] = 1; self.add[i] = 0
        if tl == tr:
            self.tot[i] = arr[tl] % MOD
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        self.tot[i] = (self.tot[2 * i] + self.tot[2 * i + 1]) % MOD
        self.mult[i] = 1
        self.add[i] = 0

    # v -> v*m + a on every slot of this node. Composition is (m1*m2, a1*m2 + a2):
    # the OLD add has to be scaled by the NEW mult, which is the step people drop.
    def _applyTag(self, i, m, a, width):
        self.tot[i] = (self.tot[i] * m + a * width) % MOD
        self.mult[i] = self.mult[i] * m % MOD
        self.add[i] = (self.add[i] * m + a) % MOD

    def _push(self, i, tl, tr):
        m = self.mult[i]; a = self.add[i]
        if m == 1 and a == 0:
            return
        tm = (tl + tr) // 2
        self._applyTag(2 * i, m, a, tm - tl + 1)
        self._applyTag(2 * i + 1, m, a, tr - tm)
        self.mult[i] = 1
        self.add[i] = 0

    def _affine(self, i, tl, tr, ql, qr, m, a):
        if qr < tl or ql > tr:
            return
        if ql <= tl and qr >= tr:
            self._applyTag(i, m, a, tr - tl + 1)
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._affine(2 * i, tl, tm, ql, qr, m, a)
        self._affine(2 * i + 1, tm + 1, tr, ql, qr, m, a)
        self._pull(i)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return 0
        if ql <= tl and qr >= tr:
            return self.tot[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        return (self._sum(2 * i, tl, tm, ql, qr) + self._sum(2 * i + 1, tm + 1, tr, ql, qr)) % MOD

    def _set(self, i, tl, tr, p, v):
        if tl == tr:
            self.tot[i] = v; self.mult[i] = 1; self.add[i] = 0
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        if p <= tm: self._set(2 * i, tl, tm, p, v)
        else: self._set(2 * i + 1, tm + 1, tr, p, v)
        self._pull(i)

    ################ PUBLIC METHODS START HERE ################

    # O(log n) -- a[i] = a[i]*m + x for every i in l...r. every other update is this one
    def rangeAffine(self, l, r, m, x):
        if l > r or not self.n:
            return
        self._affine(1, 0, self.n - 1, l, r, m % MOD, x % MOD)

    # O(log n) -- a[i] += x
    def rangeAdd(self, l, r, x):
        self.rangeAffine(l, r, 1, x)

    # O(log n) -- a[i] *= m
    def rangeMult(self, l, r, m):
        self.rangeAffine(l, r, m, 0)

    # O(log n) -- a[i] = x. multiplying by 0 then adding x, no separate tag needed
    def rangeAssign(self, l, r, x):
        self.rangeAffine(l, r, 0, x)

    # O(log n) -- sum of l...r, mod MOD
    def rangeSum(self, l, r):
        return 0 if (l > r or not self.n) else self._sum(1, 0, self.n - 1, l, r)

    # O(log n) -- a[pos] = v, an OVERWRITE that discards every pending tag on that slot
    def pointSet(self, pos, v):
        if self.n:
            self._set(1, 0, self.n - 1, pos, v % MOD)

    # O(log n)
    def pointGet(self, pos):
        return self.rangeSum(pos, pos)