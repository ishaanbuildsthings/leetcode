# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeMin rangeSum
# @data-structure-type: beats
# @complexities:
#   pointAdd: log(U)*log(U) amortized
#   pointAssign: log(U)*log(U) amortized
#   pointChmax: log(U)*log(U) amortized
#   pointChmin: log(U)*log(U) amortized
#   pointGet: log(U)
#   rangeAdd: log(U)*log(U) amortized
#   rangeAssign: log(U)*log(U) amortized
#   rangeChmax: log(U)*log(U) amortized
#   rangeMin: log(U)
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mn[4*log(U)] mn2[4*log(U)] cntMn[4*log(U)] tot[4*log(U)] sz[4*log(U)]
#   tags: addMn[4*log(U)] addOther[4*log(U)] hasAssign[4*log(U)] assignVal[4*log(U)]
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
# BeatsChmax_PERFORMANT(arr)

# AMORTIZED O(logN):     rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
# AMORTIZED O(logN):     rangeAssign(l, r, x)   -- a[i] = x
# AMORTIZED O(logN):     pointAssign(pos, newVal)  -- OVERWRITE, may RAISE the value
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
pointAssign can raise a value, injecting at most logN distinct values (one per node on its path), so
Q of them add Q logN. The bound stays O((n + q) logN).
"""

# ========================



POS_INF = float('inf')


class SparseBeatsChmax:
    # O(1) -- all zeros over [lo, hi]; any range of integers works
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        # node 0 is unused; node 1 is the root, one block of hi - lo + 1 zeros
        self.L, self.R, self.ln = [0, 0], [0, 0], [0, 0]
        self.mn = [0] * 2
        self.mn2 = [POS_INF] * 2
        self.cntMn = [0] * 2
        self.tot = [0] * 2
        self.sz = [0] * 2
        self.addMn = [0] * 2
        self.addOther = [0] * 2
        self.hasAssign = [False] * 2
        self.assignVal = [0] * 2
        self._zero(1, hi - lo + 1)

    # node i becomes a block of k zeros (its defaults, plus every count = k)
    def _zero(self, i, k):
        self.ln[i] = k
        self.cntMn[i] = k
        self.sz[i] = k

    # a fresh node: a block of k zeros
    def _node(self, k):
        j = len(self.L)
        self.L.append(0)
        self.R.append(0)
        self.ln.append(0)
        self.mn.append(0)
        self.mn2.append(POS_INF)
        self.cntMn.append(0)
        self.tot.append(0)
        self.sz.append(0)
        self.addMn.append(0)
        self.addOther.append(0)
        self.hasAssign.append(False)
        self.assignVal.append(0)
        self._zero(j, k)
        return j

    # create node i's children (blocks of zeros: the left one gets the extra slot) if it has none yet
    def _kids(self, i):
        if not self.L[i] and self.ln[i] > 1:
            k = self.ln[i]
            self.L[i] = self._node((k + 1) // 2)
            self.R[i] = self._node(k // 2)

    def _pull(self, i):
        l = self.L[i]; r = self.R[i]
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
        self._kids(i)
        if self.sz[i] == 1:
            return
        l = self.L[i]; r = self.R[i]
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
        self._kids(i)
        tm = (tl + tr) // 2
        self._chmax(self.L[i], tl, tm, ql, qr, x)
        self._chmax(self.R[i], tm + 1, tr, ql, qr, x)
        self._pull(i)

    def rangeChmax(self, l, r, x):
        if l <= r:
            self._chmax(1, self.lo, self.hi, l, r, x)

    def _add(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr:
            return
        if ql <= tl and qr >= tr:
            self._applyAdd(i, v, v)
            return
        self._push(i)
        self._kids(i)
        tm = (tl + tr) // 2
        self._add(self.L[i], tl, tm, ql, qr, v)
        self._add(self.R[i], tm + 1, tr, ql, qr, v)
        self._pull(i)

    def rangeAdd(self, l, r, v):
        if l <= r:
            self._add(1, self.lo, self.hi, l, r, v)

    def _assign(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr:
            return
        if ql <= tl and qr >= tr:
            self._applyAssign(i, v)
            return
        self._push(i)
        self._kids(i)
        tm = (tl + tr) // 2
        self._assign(self.L[i], tl, tm, ql, qr, v)
        self._assign(self.R[i], tm + 1, tr, ql, qr, v)
        self._pull(i)

    def rangeAssign(self, l, r, v):
        if l <= r:
            self._assign(1, self.lo, self.hi, l, r, v)

    def pointAssign(self, pos, v):
        self.rangeAssign(pos, pos, v)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return 0
        if ql <= tl and qr >= tr:
            return self.tot[i]
        self._push(i)
        self._kids(i)
        tm = (tl + tr) // 2
        return self._sum(self.L[i], tl, tm, ql, qr) + self._sum(self.R[i], tm + 1, tr, ql, qr)

    def rangeSum(self, l, r):
        return 0 if (l > r) else self._sum(1, self.lo, self.hi, l, r)

    def _qmin(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr:
            return POS_INF
        if ql <= tl and qr >= tr:
            return self.mn[i]
        self._push(i)
        self._kids(i)
        tm = (tl + tr) // 2
        a = self._qmin(self.L[i], tl, tm, ql, qr)
        b = self._qmin(self.R[i], tm + 1, tr, ql, qr)
        return a if a < b else b

    def rangeMin(self, l, r):
        return POS_INF if (l > r) else self._qmin(1, self.lo, self.hi, l, r)

    def pointGet(self, pos):
        return self.rangeMin(pos, pos)

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        self.rangeChmax(i, i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAdd(i, i, delta)
