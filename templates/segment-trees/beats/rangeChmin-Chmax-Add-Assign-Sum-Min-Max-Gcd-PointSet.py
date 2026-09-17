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
# AMORTIZED O(logN):     pointSet(pos, newVal)  -- OVERWRITE, may RAISE the value
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


class BeatsGcd_PERFORMANT:
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
        self.diffGcd = [0] * size
        self.addTag = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        if tl == tr:
            v = arr[tl]
            self.mx[i] = v; self.mx2[i] = NEG_INF; self.cntMx[i] = 1
            self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = 1
            self.tot[i] = v; self.diffGcd[i] = 0; self.addTag[i] = 0
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
        if tl == tr: return
        tm = (tl + tr) // 2
        lsz = tm - tl + 1; rsz = tr - tm
        l = 2 * i; r = l + 1
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
        tm = (tl + tr) // 2
        self._chmin(2 * i, tl, tm, ql, qr, x)
        self._chmin(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    def rangeChmin(self, l, r, x):
        if l <= r and self.n: self._chmin(1, 0, self.n - 1, l, r, x)

    def _chmax(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x <= self.mn[i]: return
        if ql <= tl and qr >= tr and x < self.mn2[i]:
            self._applyChmax(i, tr - tl + 1, x); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._chmax(2 * i, tl, tm, ql, qr, x)
        self._chmax(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    def rangeChmax(self, l, r, x):
        if l <= r and self.n: self._chmax(1, 0, self.n - 1, l, r, x)

    def _add(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr: return
        if ql <= tl and qr >= tr:
            self._applyAdd(i, tr - tl + 1, v); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._add(2 * i, tl, tm, ql, qr, v)
        self._add(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    def rangeAdd(self, l, r, v):
        if l <= r and self.n: self._add(1, 0, self.n - 1, l, r, v)

    def _assign(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr: return
        if ql <= tl and qr >= tr:
            self._applyAssign(i, tr - tl + 1, v); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._assign(2 * i, tl, tm, ql, qr, v)
        self._assign(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    def rangeAssign(self, l, r, v):
        if l <= r and self.n: self._assign(1, 0, self.n - 1, l, r, v)

    def pointSet(self, p, v):
        self.rangeAssign(p, p, v)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return 0
        if ql <= tl and qr >= tr: return self.tot[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        return self._sum(2 * i, tl, tm, ql, qr) + self._sum(2 * i + 1, tm + 1, tr, ql, qr)

    def rangeSum(self, l, r):
        return 0 if (l > r or not self.n) else self._sum(1, 0, self.n - 1, l, r)

    def _qmax(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return NEG_INF
        if ql <= tl and qr >= tr: return self.mx[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._qmax(2 * i, tl, tm, ql, qr)
        b = self._qmax(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a > b else b

    def rangeMax(self, l, r):
        return NEG_INF if (l > r or not self.n) else self._qmax(1, 0, self.n - 1, l, r)

    def _qmin(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return POS_INF
        if ql <= tl and qr >= tr: return self.mn[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._qmin(2 * i, tl, tm, ql, qr)
        b = self._qmin(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a < b else b

    def rangeMin(self, l, r):
        return POS_INF if (l > r or not self.n) else self._qmin(1, 0, self.n - 1, l, r)

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
        tm = (tl + tr) // 2
        return gcd(self._qgcd(2 * i, tl, tm, ql, qr), self._qgcd(2 * i + 1, tm + 1, tr, ql, qr))

    def rangeGcd(self, l, r):
        return 0 if (l > r or not self.n) else self._qgcd(1, 0, self.n - 1, l, r)