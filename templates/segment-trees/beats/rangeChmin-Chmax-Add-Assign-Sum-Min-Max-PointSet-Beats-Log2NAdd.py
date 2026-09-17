# TEMPLATE BY https://github.com/agrawalishaan

# ========================
# COMPLEXITIES

# O(n) build
# BeatsChminChmax_PERFORMANT(arr)

# AMORTIZED O(logN):     rangeChmin(l, r, x)    -- a[i] = min(a[i], x)
# AMORTIZED O(logN):     rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
# AMORTIZED O(logN):     rangeAssign(l, r, x)   -- a[i] = x
# AMORTIZED O(logN):     pointSet(pos, newVal)  -- OVERWRITE, may RAISE the value
# AMORTIZED O(log^2 N):  rangeAdd(l, r, x)      -- a[i] += x

# O(logN):  rangeSum(l, r)
# O(logN):  rangeMin(l, r)
# O(logN):  rangeMax(l, r)
# O(logN):  pointGet(pos)
# O(n) space

# IF YOU NEVER CALL rangeAdd, the whole structure is O((n + q) logN).
# The moment rangeAdd is in the mix EVERYTHING becomes O((n + q) log^2 N). That log^2 was proven
# TIGHT by Tony2_CF in Dec 2025 (codeforces.com/blog/entry/149516).

# This is the ONE-LOG CEILING for a segment tree: every clamp op plus assign plus every aggregate,
# minus range add. If you only need one side, the Chmin-only / Chmax-only variants have half the
# node and none of the cross-interaction code below.

# NOT A PLAIN MERGE OF THE TWO ONE-SIDED VARIANTS. Holding both sides in one node needs glue that
# neither one-sided version has:
#   - a node with ONE distinct value has mx == mn, so the max group and the min group are the SAME
#     group. _applyAdd branches on this and folds the three deltas with (vMax + vMin - vOther),
#     which collapses correctly for a plain add (v+v-v = v), for a chmin (d+0-0 = d), and for a
#     chmax (0+d-0 = d).
#   - with exactly TWO distinct values, mx2 == mn and mn2 == mx, so the second-max belongs to the
#     MIN group and the second-min belongs to the MAX group. They must move with their own group,
#     not with "other". That is what the two ternaries in _applyAdd are for.
# These only fire when the two sides meet, which random tests hit rarely -- stress test it if you
# touch this.

# Values may be negative. Python ints are arbitrary precision so there is nothing to overflow. Sentinels are float infinities, which absorb add tags
# correctly.

# ========================
"""
HOW DO POTENTIALS WORK? (segment tree beats)

Think about the "potential" of the entire segment tree. Each of the N values appears in logN
nodes, so the tree captures N logN element-slots. A node's potential is the number of DISTINCT
values in its interval, so the potential across the whole tree is at most N logN.

chmin / chmax / assign can never RAISE this. They apply the SAME function to every element of a
covered node, and a function can merge two distinct values into one but can never split one value
into two. That is the whole requirement -- it is not about monotonicity.

There are 3 types of nodes in a seg tree:

1) STRADDLES THE QUERY RANGE (always recurses)
at most 2*logN visited per query

2) DEAD-END NODE (does not recurse)
always comes from one of the other nodes so these are free

3) FULLY COVERED NODES THAT DO RECURSE
in a normal segment tree we stop as soon as we hit one, here we do not
We must show the # of fully covered nodes we visit is bounded, as the others are bounded, then
our total visits is bounded

For a chmin with value x at a fully covered node:
  case 1, x >= mx           -- nothing here is above x, return immediately (this falls into case 2)
  case 2, mx2 < x < mx      -- ONLY the copies of the max move, and they all move to x. We know how
                               many there are (cntMx) so we can patch the sum in O(1) and return.
                               Nothing got glued, so NO potential was spent -- which is exactly why
                               we are not allowed to descend here, and exactly why we need a lazy
                               tag: we fixed this node but left its children stale.
  case 3, x <= mx2          -- mx and mx2 both land on x, so two distinct values get GLUED together
                               and this node's potential drops by at least one, paying for the visit.
                               We recurse to the children.

So we can only descend when potential actually drops. (Contrast rangeMod, where the prune test and
the potential test are the SAME test -- max >= mod always means a real halving is waiting below --
so you can always descend and never need a lazy tag at all.)

RANGE ADD IS THE ONE THAT BREAKS IT:
A node fully inside the add range has every value shifted by the same amount, so its distinct count
is unchanged. A node fully outside is untouched. But a node STRADDLING the boundary gets half its
elements shifted and half not, so two different functions are applied and equal values come apart.
Each add creates O(logN) such boundary nodes, so the potential refills and the distinct-value
argument dies. jiry_2 switches to a TAG-BASED potential there, which gives O((n + q) log^2 N).
Tony2_CF proved in Dec 2025 that this log^2 is TIGHT -- it is not a gap in the proof.

POINT SET / ASSIGN:
assign collapses a covered node to one distinct value, so it DRAINS potential; it is free.
pointSet can raise a value, injecting at most logN distinct values (one per node on its path), so
Q of them add Q logN. The bound stays O((n + q) logN).
"""

# ========================



NEG_INF = float('-inf')
POS_INF = float('inf')


class BeatsChminChmax_PERFORMANT:
    def __init__(self, arr):
        self.n = n = len(arr)
        size = 4 * max(1, n)
        self.mx = [0] * size
        self.mx2 = [NEG_INF] * size
        self.cntMx = [0] * size
        self.mn = [0] * size
        self.mn2 = [POS_INF] * size
        self.cntMn = [0] * size
        self.tot = [0] * size
        self.sz = [0] * size
        self.addMx = [0] * size
        self.addMn = [0] * size
        self.addOther = [0] * size
        self.hasAssign = [False] * size
        self.assignVal = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        if tl == tr:
            v = arr[tl]
            self.mx[i] = v; self.mn[i] = v
            self.mx2[i] = NEG_INF; self.mn2[i] = POS_INF
            self.cntMx[i] = 1; self.cntMn[i] = 1
            self.tot[i] = v; self.sz[i] = 1
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        l = 2 * i; r = l + 1
        mx = self.mx; mx2 = self.mx2; cntMx = self.cntMx
        mn = self.mn; mn2 = self.mn2; cntMn = self.cntMn
        self.sz[i] = self.sz[l] + self.sz[r]
        self.tot[i] = self.tot[l] + self.tot[r]
        if mx[l] > mx[r]:
            mx[i] = mx[l]; cntMx[i] = cntMx[l]
            mx2[i] = mx2[l] if mx2[l] > mx[r] else mx[r]
        elif mx[l] < mx[r]:
            mx[i] = mx[r]; cntMx[i] = cntMx[r]
            mx2[i] = mx2[r] if mx2[r] > mx[l] else mx[l]
        else:
            mx[i] = mx[l]; cntMx[i] = cntMx[l] + cntMx[r]
            mx2[i] = mx2[l] if mx2[l] > mx2[r] else mx2[r]
        if mn[l] < mn[r]:
            mn[i] = mn[l]; cntMn[i] = cntMn[l]
            mn2[i] = mn2[l] if mn2[l] < mn[r] else mn[r]
        elif mn[l] > mn[r]:
            mn[i] = mn[r]; cntMn[i] = cntMn[r]
            mn2[i] = mn2[r] if mn2[r] < mn[l] else mn[l]
        else:
            mn[i] = mn[l]; cntMn[i] = cntMn[l] + cntMn[r]
            mn2[i] = mn2[l] if mn2[l] < mn2[r] else mn2[r]
        self.hasAssign[i] = False
        self.addMx[i] = 0; self.addMn[i] = 0; self.addOther[i] = 0

    def _applyAdd(self, i, vMax, vMin, vOther):
        if self.mx[i] == self.mn[i]:
            d = vMax + vMin - vOther
            self.tot[i] += d * self.sz[i]
            self.mx[i] += d
            self.mn[i] = self.mx[i]
            if self.hasAssign[i]:
                self.assignVal[i] = self.mx[i]
            else:
                self.addMx[i] += d; self.addMn[i] += d; self.addOther[i] += d
            return
        self.tot[i] += (vMax * self.cntMx[i] + vMin * self.cntMn[i]
                        + vOther * (self.sz[i] - self.cntMx[i] - self.cntMn[i]))
        if self.mx2[i] != NEG_INF:
            self.mx2[i] += vMin if self.mx2[i] == self.mn[i] else vOther
        if self.mn2[i] != POS_INF:
            self.mn2[i] += vMax if self.mn2[i] == self.mx[i] else vOther
        self.mx[i] += vMax
        self.mn[i] += vMin
        self.addMx[i] += vMax; self.addMn[i] += vMin; self.addOther[i] += vOther

    def _applyAssign(self, i, v):
        sz = self.sz[i]
        self.mx[i] = v; self.mn[i] = v
        self.mx2[i] = NEG_INF; self.mn2[i] = POS_INF
        self.cntMx[i] = sz; self.cntMn[i] = sz
        self.tot[i] = v * sz
        self.addMx[i] = 0; self.addMn[i] = 0; self.addOther[i] = 0
        self.hasAssign[i] = True; self.assignVal[i] = v

    def _push(self, i):
        if self.sz[i] == 1:
            return
        l = 2 * i; r = l + 1
        if self.hasAssign[i]:
            v = self.assignVal[i]
            self._applyAssign(l, v)
            self._applyAssign(r, v)
            self.hasAssign[i] = False
            return
        aMx = self.addMx[i]; aMn = self.addMn[i]; aO = self.addOther[i]
        if aMx == 0 and aMn == 0 and aO == 0:
            return
        mxc = self.mx[l] if self.mx[l] > self.mx[r] else self.mx[r]
        mnc = self.mn[l] if self.mn[l] < self.mn[r] else self.mn[r]
        for c in (l, r):
            self._applyAdd(c,
                           aMx if self.mx[c] == mxc else aO,
                           aMn if self.mn[c] == mnc else aO,
                           aO)
        self.addMx[i] = 0; self.addMn[i] = 0; self.addOther[i] = 0

    # ---- chmin ----
    def _chmin(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x >= self.mx[i]:
            return
        if ql <= tl and qr >= tr and x > self.mx2[i]:
            self._applyAdd(i, x - self.mx[i], 0, 0)
            return
        self._push(i)
        tm = (tl + tr) // 2
        self._chmin(2 * i, tl, tm, ql, qr, x)
        self._chmin(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    def rangeChmin(self, l, r, x):
        if l > r or self.n == 0:
            return
        self._chmin(1, 0, self.n - 1, l, r, x)

    # ---- chmax ----
    def _chmax(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x <= self.mn[i]:
            return
        if ql <= tl and qr >= tr and x < self.mn2[i]:
            self._applyAdd(i, 0, x - self.mn[i], 0)
            return
        self._push(i)
        tm = (tl + tr) // 2
        self._chmax(2 * i, tl, tm, ql, qr, x)
        self._chmax(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    def rangeChmax(self, l, r, x):
        if l > r or self.n == 0:
            return
        self._chmax(1, 0, self.n - 1, l, r, x)

    # ---- add ----
    def _add(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr:
            return
        if ql <= tl and qr >= tr:
            self._applyAdd(i, v, v, v)
            return
        self._push(i)
        tm = (tl + tr) // 2
        self._add(2 * i, tl, tm, ql, qr, v)
        self._add(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    def rangeAdd(self, l, r, v):
        if l > r or self.n == 0:
            return
        self._add(1, 0, self.n - 1, l, r, v)

    # ---- assign ----
    def _assign(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr:
            return
        if ql <= tl and qr >= tr:
            self._applyAssign(i, v)
            return
        self._push(i)
        tm = (tl + tr) // 2
        self._assign(2 * i, tl, tm, ql, qr, v)
        self._assign(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    def rangeAssign(self, l, r, v):
        if l > r or self.n == 0:
            return
        self._assign(1, 0, self.n - 1, l, r, v)

    def pointSet(self, pos, v):
        self.rangeAssign(pos, pos, v)

    # ---- queries ----
    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return 0
        if ql <= tl and qr >= tr:
            return self.tot[i]
        self._push(i)
        tm = (tl + tr) // 2
        return self._sum(2 * i, tl, tm, ql, qr) + self._sum(2 * i + 1, tm + 1, tr, ql, qr)

    def rangeSum(self, l, r):
        if l > r or self.n == 0:
            return 0
        return self._sum(1, 0, self.n - 1, l, r)

    def _max(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return NEG_INF
        if ql <= tl and qr >= tr:
            return self.mx[i]
        self._push(i)
        tm = (tl + tr) // 2
        a = self._max(2 * i, tl, tm, ql, qr)
        b = self._max(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a > b else b

    def rangeMax(self, l, r):
        if l > r or self.n == 0:
            return NEG_INF
        return self._max(1, 0, self.n - 1, l, r)

    def _min(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return POS_INF
        if ql <= tl and qr >= tr:
            return self.mn[i]
        self._push(i)
        tm = (tl + tr) // 2
        a = self._min(2 * i, tl, tm, ql, qr)
        b = self._min(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a < b else b

    def rangeMin(self, l, r):
        if l > r or self.n == 0:
            return POS_INF
        return self._min(1, 0, self.n - 1, l, r)

    def pointGet(self, pos):
        return self.rangeMax(pos, pos)