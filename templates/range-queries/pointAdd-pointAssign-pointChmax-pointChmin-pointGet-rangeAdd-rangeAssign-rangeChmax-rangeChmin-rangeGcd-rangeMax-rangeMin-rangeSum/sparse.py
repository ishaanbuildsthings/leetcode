# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeGcd rangeMax rangeMin rangeSum
# @data-structure-type: beats
# @complexities:
#   pointAdd: log(U)*log(U)*log(U) amortized ?
#   pointAssign: log(U)*log(U)*log(U) amortized ?
#   pointChmax: log(U)*log(U)*log(U) amortized ?
#   pointChmin: log(U)*log(U)*log(U) amortized ?
#   pointGet: log(U)
#   rangeAdd: log(U)*log(U)*log(U) amortized ?
#   rangeAssign: log(U)*log(U)*log(U) amortized ?
#   rangeChmax: log(U)*log(U)*log(U) amortized ?
#   rangeChmin: log(U)*log(U)*log(U) amortized ?
#   rangeGcd: log(U)*log(U) ?
#   rangeMax: log(U)
#   rangeMin: log(U)
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mx[4*log(U)] mx2[4*log(U)] cntMx[4*log(U)] mn[4*log(U)] mn2[4*log(U)] cntMn[4*log(U)] tot[4*log(U)] diffGcd[4*log(U)]
#   tags: addTag[4*log(U)]
#   other: none
#   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. C++: one shared node pool, call resetPool() between test cases; Python: per-node lists that grow

# Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
# is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
# right before anything descends past a node or pushes its tags. Otherwise the beats logic below is the
# dense tree's, with children in L / R instead of at 2i / 2i + 1.

# TEMPLATE BY https://github.com/agrawalishaan
#
# ========================
# COMPLEXITIES
#
# O(n) build
# seg = BeatsGcd_PERFORMANT(arr)
#
# AMORTIZED O(logN):     rangeChmin(l, r, x)    -- a[i] = min(a[i], x)
# AMORTIZED O(logN):     rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
# AMORTIZED O(logN):     rangeAssign(l, r, x)   -- a[i] = x
# AMORTIZED O(logN):     pointAssign(pos, newVal)  -- OVERWRITE, may RAISE the value
# AMORTIZED O(log^2 N):  rangeAdd(l, r, x)      -- a[i] += x
#
# O(logN):          rangeSum(l, r)
# O(logN):          rangeMin(l, r)
# O(logN):          rangeMax(l, r)
# O(logN):          pointGet(pos)
# O(logN * logC):   rangeGcd(l, r)      -- the extra logC is the Euclid calls
# O(n) space
#
# IF YOU NEVER CALL rangeAdd the whole structure is O((n + q) logN); with it, O((n + q) log^2 N),
# and that log^2 is proven tight (Tony2_CF, Dec 2025, codeforces.com/blog/entry/149516).
#
# HOW THE GCD WORKS -- the point is that DIFFERENCES ARE INVARIANT UNDER A UNIFORM ADD.
# gcd of a set equals gcd(any one element, all the pairwise differences). So split the node's values
# into three groups: the copies of the max, the copies of the min, and everything strictly between,
# which we call the INTERIOR. chmin only ever moves the max group and chmax only ever moves the min
# group, so the interior values are only ever SHIFTED, all by the same amount -- which means their
# pairwise differences never change at all. diffGcd holds a spanning tree of those differences and
# _applyAdd does not touch it.
#
# At query time we rebuild the full gcd from three bridges:
#     diffGcd                 the interior, already joined up
#     gcd with (mx2 - mx)     bridges the max group in, since mx2 is the largest interior value
#     gcd with (mn2 - mn)     bridges the min group in
#     gcd with mx             anchors the whole thing on an actual element rather than a difference
# _pull is where the bookkeeping lives: a value that was a child's max or min may be INTERIOR in the
# parent, so it has to be folded into the parent's spanning tree, and the two children's trees have
# to be joined to each other. That is what the hasL / hasR / any dance is doing.
#
# WHY THE TAGS ARE JUST ONE ADD PLUS mx AND mn:
# any sequence of add / chmin / chmax on a whole node composes to min(a, max(b, x + c)), so one add
# tag and two clamp bounds is the complete closed form -- there is no need for per-group add tags.
# And the two clamp bounds are already stored: a is the node's mx and b is its mn, because for every
# value actually in the node, clamping to [mn, mx] gives the same answer as clamping to [b, a].
# There is no assign tag either -- an assign leaves mn == mx, and mn == mx already means "every value
# here is this number", so _push just forwards that to both children as an assign.
#
# STILL NEEDS THE CROSS-INTERACTION GLUE (only fires when the two sides meet, so stress test it):
#   - a chmin whose value lands at or below mn collapses the node, so it becomes an assign
#   - a chmin on a node with EXACTLY TWO distinct values has mn2 == mx, so the second-min is the
#     thing being clamped and mn2 must follow the max down
#   - and the mirror of both for chmax
#
# Verified against the official sample of "Minimize, Add, GCD and Their Friends" and against brute
# force. At n = q = 200000 the C++ version runs in about 0.24s; this Python one will NOT
# hold a 4s limit at that size, it is here for smaller inputs and for reading.
#
# Values are assumed POSITIVE (the source problem gives 1 <= a[i] <= 1e9 and x >= 1). gcd is taken
# on absolute values so negatives will not crash, but they are untested.
#
# ========================
#
from math import gcd

NEG_INF = float('-inf')
POS_INF = float('inf')


class SparseBeatsGcd:
    # O(1) -- all zeros over [lo, hi]; any range of integers works
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        # node 0 is unused; node 1 is the root, one block of hi - lo + 1 zeros
        self.L, self.R, self.ln = [0, 0], [0, 0], [0, 0]
        self.mx = [0] * 2
        self.mx2 = [NEG_INF] * 2
        self.cntMx = [0] * 2
        self.mn = [0] * 2
        self.mn2 = [POS_INF] * 2
        self.cntMn = [0] * 2
        self.tot = [0] * 2
        self.diffGcd = [0] * 2
        self.addTag = [0] * 2
        self._zero(1, hi - lo + 1)

    # node i becomes a block of k zeros (its defaults, plus every count = k)
    def _zero(self, i, k):
        self.ln[i] = k
        self.cntMx[i] = k
        self.cntMn[i] = k

    # a fresh node: a block of k zeros
    def _node(self, k):
        j = len(self.L)
        self.L.append(0)
        self.R.append(0)
        self.ln.append(0)
        self.mx.append(0)
        self.mx2.append(NEG_INF)
        self.cntMx.append(0)
        self.mn.append(0)
        self.mn2.append(POS_INF)
        self.cntMn.append(0)
        self.tot.append(0)
        self.diffGcd.append(0)
        self.addTag.append(0)
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

        g = gcd(self.diffGcd[l], self.diffGcd[r])
        aMx2 = mx2[l]; bMx2 = mx2[r]
        hasL = aMx2 != NEG_INF and aMx2 != mn[l]
        hasR = bMx2 != NEG_INF and bMx2 != mn[r]
        if hasL and hasR:
            g = gcd(g, abs(aMx2 - bMx2))
        if hasL:
            any_ = aMx2; haveAny = True
        elif hasR:
            any_ = bMx2; haveAny = True
        else:
            any_ = 0; haveAny = False
        pmn = mn[i]; pmx = mx[i]
        for val in (mn[l], mx[l], mn[r], mx[r]):
            if val != pmn and val != pmx:
                if haveAny:
                    g = gcd(g, abs(val - any_))
                else:
                    any_ = val; haveAny = True
        self.diffGcd[i] = g
        self.addTag[i] = 0

    def _applyAssign(self, i, sz, v):
        self.mx[i] = v; self.mx2[i] = NEG_INF; self.cntMx[i] = sz
        self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = sz
        self.tot[i] = v * sz; self.diffGcd[i] = 0; self.addTag[i] = 0

    def _applyAdd(self, i, sz, v):
        if self.mn[i] == self.mx[i]:
            self._applyAssign(i, sz, self.mx[i] + v); return
        self.mx[i] += v
        if self.mx2[i] != NEG_INF: self.mx2[i] += v
        self.mn[i] += v
        if self.mn2[i] != POS_INF: self.mn2[i] += v
        self.tot[i] += sz * v
        self.addTag[i] += v
        # diffGcd untouched: a uniform shift does not change any difference

    def _applyChmin(self, i, sz, v):
        if self.mn[i] >= v:
            self._applyAssign(i, sz, v); return
        if self.mx[i] > v:
            if self.mn2[i] == self.mx[i]: self.mn2[i] = v
            self.tot[i] -= (self.mx[i] - v) * self.cntMx[i]
            self.mx[i] = v

    def _applyChmax(self, i, sz, v):
        if self.mx[i] <= v:
            self._applyAssign(i, sz, v); return
        if self.mn[i] < v:
            if self.mx2[i] == self.mn[i]: self.mx2[i] = v
            self.tot[i] += (v - self.mn[i]) * self.cntMn[i]
            self.mn[i] = v

    def _push(self, i, tl, tr):
        self._kids(i)
        if tl == tr: return
        self._kids(i)
        tm = (tl + tr) // 2
        lsz = tm - tl + 1; rsz = tr - tm
        l = self.L[i]; r = self.R[i]
        if self.mn[i] == self.mx[i]:
            v = self.mx[i]
            self._applyAssign(l, lsz, v); self._applyAssign(r, rsz, v)
            return
        a = self.addTag[i]
        if a:
            self._applyAdd(l, lsz, a); self._applyAdd(r, rsz, a)
            self.addTag[i] = 0
        self._applyChmin(l, lsz, self.mx[i]); self._applyChmin(r, rsz, self.mx[i])
        self._applyChmax(l, lsz, self.mn[i]); self._applyChmax(r, rsz, self.mn[i])

    def _chmin(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x >= self.mx[i]: return
        if ql <= tl and qr >= tr and x > self.mx2[i]:
            self._applyChmin(i, tr - tl + 1, x); return
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        self._chmin(self.L[i], tl, tm, ql, qr, x)
        self._chmin(self.R[i], tm + 1, tr, ql, qr, x)
        self._pull(i)

    def rangeChmin(self, l, r, x):
        if l <= r: self._chmin(1, self.lo, self.hi, l, r, x)

    def _chmax(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x <= self.mn[i]: return
        if ql <= tl and qr >= tr and x < self.mn2[i]:
            self._applyChmax(i, tr - tl + 1, x); return
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        self._chmax(self.L[i], tl, tm, ql, qr, x)
        self._chmax(self.R[i], tm + 1, tr, ql, qr, x)
        self._pull(i)

    def rangeChmax(self, l, r, x):
        if l <= r: self._chmax(1, self.lo, self.hi, l, r, x)

    def _add(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr: return
        if ql <= tl and qr >= tr:
            self._applyAdd(i, tr - tl + 1, v); return
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        self._add(self.L[i], tl, tm, ql, qr, v)
        self._add(self.R[i], tm + 1, tr, ql, qr, v)
        self._pull(i)

    def rangeAdd(self, l, r, v):
        if l <= r: self._add(1, self.lo, self.hi, l, r, v)

    def _assign(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr: return
        if ql <= tl and qr >= tr:
            self._applyAssign(i, tr - tl + 1, v); return
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        self._assign(self.L[i], tl, tm, ql, qr, v)
        self._assign(self.R[i], tm + 1, tr, ql, qr, v)
        self._pull(i)

    def rangeAssign(self, l, r, v):
        if l <= r: self._assign(1, self.lo, self.hi, l, r, v)

    def pointAssign(self, p, v):
        self.rangeAssign(p, p, v)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return 0
        if ql <= tl and qr >= tr: return self.tot[i]
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        return self._sum(self.L[i], tl, tm, ql, qr) + self._sum(self.R[i], tm + 1, tr, ql, qr)

    def rangeSum(self, l, r):
        return 0 if (l > r) else self._sum(1, self.lo, self.hi, l, r)

    def _qmax(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return NEG_INF
        if ql <= tl and qr >= tr: return self.mx[i]
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        a = self._qmax(self.L[i], tl, tm, ql, qr)
        b = self._qmax(self.R[i], tm + 1, tr, ql, qr)
        return a if a > b else b

    def rangeMax(self, l, r):
        return NEG_INF if (l > r) else self._qmax(1, self.lo, self.hi, l, r)

    def _qmin(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return POS_INF
        if ql <= tl and qr >= tr: return self.mn[i]
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        a = self._qmin(self.L[i], tl, tm, ql, qr)
        b = self._qmin(self.R[i], tm + 1, tr, ql, qr)
        return a if a < b else b

    def rangeMin(self, l, r):
        return POS_INF if (l > r) else self._qmin(1, self.lo, self.hi, l, r)

    def pointGet(self, p):
        return self.rangeMax(p, p)

    def _nodeGcd(self, i):
        ans = self.diffGcd[i]
        if self.mx2[i] != NEG_INF: ans = gcd(ans, abs(self.mx2[i] - self.mx[i]))
        if self.mn2[i] != POS_INF: ans = gcd(ans, abs(self.mn2[i] - self.mn[i]))
        return gcd(ans, abs(self.mx[i]))

    def _qgcd(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return 0
        if ql <= tl and qr >= tr: return self._nodeGcd(i)
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        return gcd(self._qgcd(self.L[i], tl, tm, ql, qr), self._qgcd(self.R[i], tm + 1, tr, ql, qr))

    def rangeGcd(self, l, r):
        return 0 if (l > r) else self._qgcd(1, self.lo, self.hi, l, r)

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        self.rangeChmax(i, i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        self.rangeChmin(i, i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAdd(i, i, delta)