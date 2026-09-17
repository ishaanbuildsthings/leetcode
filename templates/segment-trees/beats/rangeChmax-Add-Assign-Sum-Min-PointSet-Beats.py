# TEMPLATE BY https://github.com/agrawalishaan

# ========================
# COMPLEXITIES

# O(n) build
# BeatsChmax_PERFORMANT(arr)

# AMORTIZED O(logN):     rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
# AMORTIZED O(logN):     rangeAssign(l, r, x)   -- a[i] = x
# AMORTIZED O(logN):     pointSet(pos, newVal)  -- OVERWRITE, may RAISE the value
# AMORTIZED O(log^2 N):  rangeAdd(l, r, x)      -- a[i] += x

# O(logN):  rangeSum(l, r)
# O(logN):  rangeMin(l, r)
# O(logN):  pointGet(pos)
# O(n) space

# IF YOU NEVER CALL rangeAdd, the whole structure is O((n + q) logN).
# The moment rangeAdd is in the mix EVERYTHING becomes O((n + q) log^2 N). That log^2 was proven
# TIGHT by Tony2_CF in Dec 2025 (codeforces.com/blog/entry/149516), so it is not worth hunting for
# a one-log version. If you need a rangeMax too, use the Chmin+Chmax variant instead.

# Values may be negative. Python ints are arbitrary precision so there is nothing to overflow.
# Sentinels are float infinities, which absorb add tags correctly.

# ========================
"""
HOW DO POTENTIALS WORK? (segment tree beats)

Think about the "potential" of the entire segment tree. Each of the N values appears in logN
nodes, so the tree captures N logN element-slots. A node's potential is the number of DISTINCT
values in its interval, so the potential across the whole tree is at most N logN.

chmax / chmin / assign can never RAISE this. They apply the SAME function to every element of a
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



POS_INF = float('inf')


class BeatsChmax_PERFORMANT:
    def __init__(self, arr):
        self.n = n = len(arr)
        size = 4 * max(1, n)
        self.mn = [0] * size
        self.mn2 = [POS_INF] * size
        self.cntMn = [0] * size
        self.tot = [0] * size
        self.sz = [0] * size
        self.addMn = [0] * size
        self.addOther = [0] * size
        self.hasAssign = [False] * size
        self.assignVal = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        if tl == tr:
            v = arr[tl]
            self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = 1
            self.tot[i] = v; self.sz[i] = 1
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        l = 2 * i; r = l + 1
        mn = self.mn; mn2 = self.mn2; cntMn = self.cntMn
        self.sz[i] = self.sz[l] + self.sz[r]
        self.tot[i] = self.tot[l] + self.tot[r]
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
        self.addMn[i] = 0; self.addOther[i] = 0

    def _applyAdd(self, i, vMin, vOther):
        self.tot[i] += vMin * self.cntMn[i] + vOther * (self.sz[i] - self.cntMn[i])
        if self.mn2[i] != POS_INF:
            self.mn2[i] += vOther
        self.mn[i] += vMin
        if self.hasAssign[i]:
            self.assignVal[i] = self.mn[i]
        else:
            self.addMn[i] += vMin; self.addOther[i] += vOther

    def _applyAssign(self, i, v):
        sz = self.sz[i]
        self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = sz
        self.tot[i] = v * sz
        self.addMn[i] = 0; self.addOther[i] = 0
        self.hasAssign[i] = True; self.assignVal[i] = v

    def _push(self, i):
        if self.sz[i] == 1:
            return
        l = 2 * i; r = l + 1
        if self.hasAssign[i]:
            v = self.assignVal[i]
            self._applyAssign(l, v); self._applyAssign(r, v)
            self.hasAssign[i] = False
            return
        aMn = self.addMn[i]; aO = self.addOther[i]
        if aMn == 0 and aO == 0:
            return
        mnc = self.mn[l] if self.mn[l] < self.mn[r] else self.mn[r]
        self._applyAdd(l, aMn if self.mn[l] == mnc else aO, aO)
        self._applyAdd(r, aMn if self.mn[r] == mnc else aO, aO)
        self.addMn[i] = 0; self.addOther[i] = 0

    def _chmax(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x <= self.mn[i]:
            return
        if ql <= tl and qr >= tr and x < self.mn2[i]:
            self._applyAdd(i, x - self.mn[i], 0)
            return
        self._push(i)
        tm = (tl + tr) // 2
        self._chmax(2 * i, tl, tm, ql, qr, x)
        self._chmax(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    def rangeChmax(self, l, r, x):
        if l <= r and self.n:
            self._chmax(1, 0, self.n - 1, l, r, x)

    def _add(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr:
            return
        if ql <= tl and qr >= tr:
            self._applyAdd(i, v, v)
            return
        self._push(i)
        tm = (tl + tr) // 2
        self._add(2 * i, tl, tm, ql, qr, v)
        self._add(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    def rangeAdd(self, l, r, v):
        if l <= r and self.n:
            self._add(1, 0, self.n - 1, l, r, v)

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
        if l <= r and self.n:
            self._assign(1, 0, self.n - 1, l, r, v)

    def pointSet(self, pos, v):
        self.rangeAssign(pos, pos, v)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return 0
        if ql <= tl and qr >= tr:
            return self.tot[i]
        self._push(i)
        tm = (tl + tr) // 2
        return self._sum(2 * i, tl, tm, ql, qr) + self._sum(2 * i + 1, tm + 1, tr, ql, qr)

    def rangeSum(self, l, r):
        return 0 if (l > r or not self.n) else self._sum(1, 0, self.n - 1, l, r)

    def _qmin(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return POS_INF
        if ql <= tl and qr >= tr:
            return self.mn[i]
        self._push(i)
        tm = (tl + tr) // 2
        a = self._qmin(2 * i, tl, tm, ql, qr)
        b = self._qmin(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a < b else b

    def rangeMin(self, l, r):
        return POS_INF if (l > r or not self.n) else self._qmin(1, 0, self.n - 1, l, r)

    def pointGet(self, pos):
        return self.rangeMin(pos, pos)