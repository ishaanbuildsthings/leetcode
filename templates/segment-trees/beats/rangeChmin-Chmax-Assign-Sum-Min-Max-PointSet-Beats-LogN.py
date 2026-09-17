# TEMPLATE BY https://github.com/agrawalishaan
#
# ========================
# COMPLEXITIES
#
# O(n) build
# seg = BeatsChminChmaxNoAdd_PERFORMANT(arr)
#
# AMORTIZED O(logN):  rangeChmin(l, r, x)    -- a[i] = min(a[i], x)
# AMORTIZED O(logN):  rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
# AMORTIZED O(logN):  rangeAssign(l, r, x)   -- a[i] = x
# AMORTIZED O(logN):  pointSet(pos, newVal)  -- OVERWRITE, may RAISE the value
#
# O(logN):  rangeSum(l, r)
# O(logN):  rangeMin(l, r)
# O(logN):  rangeMax(l, r)
# O(logN):  pointGet(pos)
# O(n) space
#
# Whole structure is O((n + q) logN). THERE IS NO rangeAdd HERE ON PURPOSE -- adding it forces
# O((n + q) log^2 N), and that log^2 is proven tight (Tony2_CF, Dec 2025,
# codeforces.com/blog/entry/149516). If you need add, take the Chmin-Chmax-Add variant instead;
# measured at n = q = 300000 it runs about 1.2x slower than this file on an add-free workload,
# because its node is 104 bytes against 56 here.
#
# THE NODE CARRIES NO TAG FIELDS AT ALL. mx doubles as the pending chmin tag and mn as the pending
# chmax tag -- if a child's mx is above my mx, that IS a pending chmin, and re-pushing a value the
# child already satisfies is a no-op, so nothing needs clearing and there is no sentinel to get
# wrong. There is no assign tag either: an assign leaves the node with mn == mx, and mn == mx
# already means "every value in my interval is this number", so _push just forwards that to both
# children as an assign.
#
# NOT A PLAIN MERGE OF A CHMIN TREE AND A CHMAX TREE. Holding both sides in one node needs glue
# neither one-sided version has, and it only fires when the two sides meet -- which random tests
# hit rarely, so stress test it if you touch it:
#   - a chmin on a UNIFORM node (mn == mx) moves the min too, so mn must follow mx down
#   - a chmin on a node with EXACTLY TWO distinct values has mn2 == mx, so the second-min is the
#     thing being clamped and mn2 must follow
#   - and the mirror of both for chmax
#
# Values may be negative. Python ints are arbitrary precision so there is
# nothing to overflow; the sentinels are float infinities.
#
# ========================
#
"""
HOW DO POTENTIALS WORK? (segment tree beats)

Think about the "potential" of the entire segment tree. Each of the N values appears in logN
nodes, so the tree captures N logN element-slots. A node's potential is the number of DISTINCT
values in its interval, so the potential across the whole tree is at most N logN.

chmin / chmax / assign can never RAISE this. They apply the SAME function to every element of a
covered node, and a function can merge two distinct values into one but can never split one value
into two. That is the whole requirement -- it is not about monotonicity. (Range add is the one
that breaks it, because at a node STRADDLING the range boundary half the elements get shifted and
half do not, so two different functions are applied and equal values come apart. That is why this
file does not have one.)

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
  case 1, x >= mx       -- nothing here is above x, return immediately (this falls into case 2)
  case 2, mx2 < x < mx  -- ONLY the copies of the max move, and they all move to x. We know how
                           many there are (cntMx) so we can patch the sum in O(1) and return.
                           cntMx does NOT change: everything below the max is at most mx2, which
                           is strictly under x, so the tie set is the same set. Nothing got glued,
                           so NO potential was spent -- which is exactly why we are not allowed to
                           descend here, and exactly why we need a tag: we fixed this node and
                           left its children stale.
  case 3, x <= mx2      -- mx and mx2 both land on x, so two distinct values get GLUED together
                           and this node's potential drops by at least one, paying for the visit.
                           We recurse to the children.

So we can only descend when potential actually drops. (Contrast rangeMod, where the prune test and
the potential test are the SAME test -- max >= mod always means a real halving is waiting below --
so you can always descend and never need a lazy tag at all.)

WHY A PUSHED TAG IS ALWAYS LEGAL:
_applyChmin has a precondition, x > mx2, that nothing in the code checks. It holds for two reasons
and they are worth writing down. Case 2 above is the ONLY place a tag is born, and it tests the
condition directly. And a parent's mx is at least its child's mx, which is strictly above the
child's mx2, so a tag that cleared the parent's bar clears the child's too. Mirror for chmax.

ASSIGN / POINT SET:
assign collapses a covered node to one distinct value, so it DRAINS potential; it is free.
pointSet can raise a value, injecting at most logN distinct values (one per node on its path), so
Q of them add Q logN. The bound stays O((n + q) logN).
"""

# ========================


NEG_INF = float('-inf')
POS_INF = float('inf')


class BeatsChminChmaxNoAdd_PERFORMANT:
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
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        if tl == tr:
            v = arr[tl]
            self.mx[i] = v; self.mx2[i] = NEG_INF; self.cntMx[i] = 1
            self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = 1
            self.tot[i] = v
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        l = 2 * i; r = l + 1
        mx = self.mx; mx2 = self.mx2; cntMx = self.cntMx
        mn = self.mn; mn2 = self.mn2; cntMn = self.cntMn
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

    def _applyChmin(self, i, x):
        if x >= self.mx[i]:
            return
        self.tot[i] -= (self.mx[i] - x) * self.cntMx[i]
        if self.mn[i] == self.mx[i]:
            self.mn[i] = x
        elif self.mn2[i] == self.mx[i]:
            self.mn2[i] = x
        self.mx[i] = x

    def _applyChmax(self, i, x):
        if x <= self.mn[i]:
            return
        self.tot[i] += (x - self.mn[i]) * self.cntMn[i]
        if self.mx[i] == self.mn[i]:
            self.mx[i] = x
        elif self.mx2[i] == self.mn[i]:
            self.mx2[i] = x
        self.mn[i] = x

    def _applyAssign(self, i, v, sz):
        self.mx[i] = v; self.mx2[i] = NEG_INF; self.cntMx[i] = sz
        self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = sz
        self.tot[i] = v * sz

    def _push(self, i, tl, tr):
        if tl == tr:
            return
        tm = (tl + tr) // 2
        l = 2 * i; r = l + 1
        if self.mn[i] == self.mx[i]:
            v = self.mx[i]
            self._applyAssign(l, v, tm - tl + 1)
            self._applyAssign(r, v, tr - tm)
            return
        self._applyChmin(l, self.mx[i]); self._applyChmin(r, self.mx[i])
        self._applyChmax(l, self.mn[i]); self._applyChmax(r, self.mn[i])

    def _chmin(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x >= self.mx[i]:
            return
        if ql <= tl and qr >= tr and x > self.mx2[i]:
            self._applyChmin(i, x); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._chmin(2 * i, tl, tm, ql, qr, x)
        self._chmin(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    def rangeChmin(self, l, r, x):
        if l <= r and self.n:
            self._chmin(1, 0, self.n - 1, l, r, x)

    def _chmax(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x <= self.mn[i]:
            return
        if ql <= tl and qr >= tr and x < self.mn2[i]:
            self._applyChmax(i, x); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._chmax(2 * i, tl, tm, ql, qr, x)
        self._chmax(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    def rangeChmax(self, l, r, x):
        if l <= r and self.n:
            self._chmax(1, 0, self.n - 1, l, r, x)

    def _assign(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr:
            return
        if ql <= tl and qr >= tr:
            self._applyAssign(i, v, tr - tl + 1); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._assign(2 * i, tl, tm, ql, qr, v)
        self._assign(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    def rangeAssign(self, l, r, v):
        if l <= r and self.n:
            self._assign(1, 0, self.n - 1, l, r, v)

    def pointSet(self, p, v):
        self.rangeAssign(p, p, v)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return 0
        if ql <= tl and qr >= tr:
            return self.tot[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        return self._sum(2 * i, tl, tm, ql, qr) + self._sum(2 * i + 1, tm + 1, tr, ql, qr)

    def rangeSum(self, l, r):
        return 0 if (l > r or not self.n) else self._sum(1, 0, self.n - 1, l, r)

    def _qmax(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return NEG_INF
        if ql <= tl and qr >= tr:
            return self.mx[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._qmax(2 * i, tl, tm, ql, qr)
        b = self._qmax(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a > b else b

    def rangeMax(self, l, r):
        return NEG_INF if (l > r or not self.n) else self._qmax(1, 0, self.n - 1, l, r)

    def _qmin(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return POS_INF
        if ql <= tl and qr >= tr:
            return self.mn[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._qmin(2 * i, tl, tm, ql, qr)
        b = self._qmin(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a < b else b

    def rangeMin(self, l, r):
        return POS_INF if (l > r or not self.n) else self._qmin(1, 0, self.n - 1, l, r)

    def pointGet(self, p):
        return self.rangeMax(p, p)