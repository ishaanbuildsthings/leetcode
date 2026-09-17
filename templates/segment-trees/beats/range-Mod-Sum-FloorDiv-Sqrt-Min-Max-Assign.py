# TEMPLATE BY https://github.com/agrawalishaan
#
# ========================
# COMPLEXITIES
#
# O(n) build
# seg = ShrinkSeg_PERFORMANT(arr)
#
# C = largest value in the array
# AMORTIZED O(logN * logC):       rangeMod(l, r, x)      -- a[i] %= x
# AMORTIZED O(logN * logC):       rangeDiv(l, r, x)      -- a[i] //= x, floor, needs x >= 2
# AMORTIZED O(logN * log(logC)):  rangeSqrt(l, r)        -- a[i] = floor(sqrt(a[i]))
# AMORTIZED O(logN):              rangeAssign(l, r, x)   -- a[i] = x
# AMORTIZED O(logN):              pointSet(pos, newVal)  -- OVERWRITE, may RAISE the value
#
# O(logN):  rangeSum(l, r)
# O(logN):  rangeMin(l, r)
# O(logN):  rangeMax(l, r)
# O(logN):  pointGet(pos)
# O(n) space
#
# Values must be NON-NEGATIVE. C++ % truncates toward zero and Python // floors toward negative
# infinity, so negatives misbehave in both, differently -- and the max-pruning hides it, because a
# subtree whose max is negative gets skipped entirely.
#
# In C++ the sum is long long, so you need n * maxValue < 9.2e18. Python ints cannot overflow.
#
# ========================
#
"""
HOW DO POTENTIALS WORK?

When we do A%B with A>=B, A always falls by at least half. If B is < half of A the result is under
B so obviously under half of A; if B is bigger than half of A then only one copy of B fits, so what
is left over is A - B which is also under half. Div and sqrt shrink too, sqrt fastest of all: if an
element still has X halvings left in it, mod or div knocks X down by one, but sqrt HALVES X, so one
element can only be sqrt'd log(logC) times before it reaches 1.

WITHOUT ASSIGN the potential is simple. Each of the N values appears in logN nodes, so the tree
captures N logN element-slots, and each value can be halved at most logC times, so the whole tree
holds N logN logC. Every fully covered node we descend into has a max at or above the cutoff, which
means a real shrink is waiting at some leaf below it, so no descent is ever wasted.

ASSIGN LOOKS LIKE IT SHOULD DESTROY THAT, AND IT WOULD, NAIVELY. Assigning a fresh value to a range
of length L hands L elements a full logC of halvings back. Q of those refill Q*N*logC, which is
worse than just walking the range every time. This is the same failure mode range-add has in the
chmin beats templates.

WHAT RESCUES IT IS THAT AN ASSIGNED NODE IS UNIFORM. If every value under a node is the same
number, then mod / div / sqrt applied to the whole node is ONE operation, not L of them -- the new
value stands for the entire subtree and we never descend into it. So the accounting stops being per
ELEMENT and becomes per RUN of equal values:
  - the array starts with at most N runs
  - each assign destroys every run inside its range and creates at most 3 (the new one, plus a
    leftover at each edge)
  - a shrink applies one function to everything it touches, and a function can merge runs but never
    split one, except at the two range edges
so across the whole run there are at most N + O(Q) runs ever, each holding logC of shrinking, and
each one costs logN to reach. That gives O((N + Q) logN logC). This is the Chtholly / ODT argument
bolted onto the beats one.

THERE IS NO ASSIGN TAG FIELD. mn == mx already means "every value in my interval is this number",
which is exactly what an assign leaves behind, so _push just forwards that to both children as an
assign. Nothing to clear, no sentinel to get wrong.

THE COST OF ADDING ASSIGN is that this template is no longer lazy-propagation-free. The old
mod/div/sqrt-only version never summarized anything at an internal node, so nothing was ever stale
and no push existed. Now every traversal that descends must _push first.

THE PRUNE CUTOFFS DIFFER BECAUSE MOD IS SELF-LIMITING AND THE OTHERS ARE NOT. After a % x the
result is strictly below x, which is exactly the thing being tested, so that leaf removes itself
from future descents. Sqrt and div shrink a value but never push it out of range of the test, so 1
would be sqrt'd forever and 0 would be divided forever. Hence cutoff 2 for sqrt and 1 for div.
"""

# ========================


from math import isqrt


class ShrinkSeg_PERFORMANT:
    def __init__(self, arr):
        self.n = n = len(arr)
        size = 4 * max(1, n)
        self.mx = [0] * size
        self.mn = [0] * size
        self.tot = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        if tl == tr:
            v = arr[tl]
            self.mx[i] = v; self.mn[i] = v; self.tot[i] = v
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        l = 2 * i; r = l + 1
        mx = self.mx; mn = self.mn
        mx[i] = mx[l] if mx[l] > mx[r] else mx[r]
        mn[i] = mn[l] if mn[l] < mn[r] else mn[r]
        self.tot[i] = self.tot[l] + self.tot[r]

    def _applyAssign(self, i, sz, v):
        self.mx[i] = v; self.mn[i] = v; self.tot[i] = v * sz

    # mn == mx IS the assign tag: a uniform node means every value below it is that number
    def _push(self, i, tl, tr):
        if tl == tr:
            return
        v = self.mx[i]
        if self.mn[i] != v:
            return
        tm = (tl + tr) // 2
        self._applyAssign(2 * i, tm - tl + 1, v)
        self._applyAssign(2 * i + 1, tr - tm, v)

    def _rangeShrink(self, i, tl, tr, ql, qr, cutoff, leafOp):
        if qr < tl or ql > tr:
            return
        if self.mx[i] < cutoff:
            return
        if ql <= tl and qr >= tr and self.mn[i] == self.mx[i]:
            self._applyAssign(i, tr - tl + 1, leafOp(self.mx[i]))
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._rangeShrink(2 * i, tl, tm, ql, qr, cutoff, leafOp)
        self._rangeShrink(2 * i + 1, tm + 1, tr, ql, qr, cutoff, leafOp)
        self._pull(i)

    def _assign(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr:
            return
        if ql <= tl and qr >= tr:
            self._applyAssign(i, tr - tl + 1, v)
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._assign(2 * i, tl, tm, ql, qr, v)
        self._assign(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return 0
        if ql <= tl and qr >= tr:
            return self.tot[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        return self._sum(2 * i, tl, tm, ql, qr) + self._sum(2 * i + 1, tm + 1, tr, ql, qr)

    def _qmax(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return None
        if ql <= tl and qr >= tr:
            return self.mx[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._qmax(2 * i, tl, tm, ql, qr)
        b = self._qmax(2 * i + 1, tm + 1, tr, ql, qr)
        if a is None: return b
        if b is None: return a
        return a if a > b else b

    def _qmin(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return None
        if ql <= tl and qr >= tr:
            return self.mn[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._qmin(2 * i, tl, tm, ql, qr)
        b = self._qmin(2 * i + 1, tm + 1, tr, ql, qr)
        if a is None: return b
        if b is None: return a
        return a if a < b else b

    ################ PUBLIC METHODS START HERE ################

    # amortized -- a[i] %= x for every i in l...r
    # prune at mx < x: everything there is already below x, so a % x == a
    def rangeMod(self, l, r, x):
        if l > r or not self.n or x < 1:
            return
        self._rangeShrink(1, 0, self.n - 1, l, r, x, lambda v: v % x)

    # amortized -- a[i] //= x for every i in l...r. requires x >= 2
    # prune at mx < 1: only zeros left, and 0 // x == 0
    def rangeDiv(self, l, r, x):
        if l > r or not self.n or x < 2:
            return
        self._rangeShrink(1, 0, self.n - 1, l, r, 1, lambda v: v // x)

    # amortized -- a[i] = floor(sqrt(a[i])) for every i in l...r
    # prune at mx < 2: 0 and 1 are fixed points
    def rangeSqrt(self, l, r):
        if l > r or not self.n:
            return
        self._rangeShrink(1, 0, self.n - 1, l, r, 2, isqrt)

    # amortized O(logN) -- a[i] = v for every i in l...r
    def rangeAssign(self, l, r, v):
        if l <= r and self.n:
            self._assign(1, 0, self.n - 1, l, r, v)

    # amortized O(logN) -- a[pos] = v. an OVERWRITE, it may RAISE the value
    def pointSet(self, pos, v):
        self.rangeAssign(pos, pos, v)

    def rangeSum(self, l, r):
        return 0 if (l > r or not self.n) else self._sum(1, 0, self.n - 1, l, r)

    def rangeMax(self, l, r):
        return None if (l > r or not self.n) else self._qmax(1, 0, self.n - 1, l, r)

    def rangeMin(self, l, r):
        return None if (l > r or not self.n) else self._qmin(1, 0, self.n - 1, l, r)

    def pointGet(self, pos):
        return self.rangeMax(pos, pos)