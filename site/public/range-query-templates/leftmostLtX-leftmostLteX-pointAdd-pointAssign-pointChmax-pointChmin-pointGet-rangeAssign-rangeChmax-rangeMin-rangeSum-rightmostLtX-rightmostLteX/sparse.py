# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmax-rangeMin-rangeSum-rightmostLtX-rightmostLteX/sparse.py
# @operations: leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeMin rangeSum rightmostLtX rightmostLteX
# @data-structure-type: beats
# @complexities:
#   leftmostLtX: log(U)
#   leftmostLteX: log(U)
#   pointAdd: log(U) amortized
#   pointAssign: log(U) amortized
#   pointChmax: log(U) amortized
#   pointChmin: log(U) amortized
#   pointGet: log(U)
#   rangeAssign: log(U) amortized
#   rangeChmax: log(U) amortized
#   rangeMin: log(U)
#   rangeSum: log(U)
#   rightmostLtX: log(U)
#   rightmostLteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mn[4*log(U)] mn2[4*log(U)] cntMn[4*log(U)] tot[4*log(U)]
#   tags: none
#   other: none
#   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. Per-node lists that grow

# Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
# is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
# right before anything descends past a node or pushes its tags. Otherwise the beats logic below is the
# dense tree's, with children in L / R instead of at 2i / 2i + 1.

# Segment tree beats: range chmax (a[i] = max(a[i], x)) and range assign, with range sums and the range min, plus
# point ops. All indices 0-based, ranges inclusive. How it works: a chmax only changes the min values of a node it
# covers, so a node keeps its min, its strict second min and how many copies of the min it has; a chmax x with mn < x
# < mn2 moves just those copies (the sum rises by (x - mn) * cntMn) and stops there, and only x >= mn2 has to go
# further down. A node's own mn doubles as its pending clamp: push clamps each child to it, so there is no chmin /
# chmax tag. There is no assign tag either: when all of a node's values are equal (no second min), push hands that
# value to both children as an assign. Amortized O(log U) per update (beats: every extra descent removes a distinct
# value).

NEG_INF = float('-inf')
POS_INF = float('inf')


class SparseChminChmaxBeats:
    # O(N)
    # O(1) -- all zeros over [lo, hi]; any range of integers works
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        # node 0 is unused; node 1 is the root, one block of hi - lo + 1 zeros
        self.L, self.R, self.ln = [0, 0], [0, 0], [0, 0]
        self.mn = [0] * 2
        self.mn2 = [POS_INF] * 2
        self.cntMn = [0] * 2
        self.tot = [0] * 2
        self._zero(1, hi - lo + 1)

    # node i becomes a block of k zeros (its defaults, plus every count = k)
    def _zero(self, i, k):
        self.ln[i] = k
        self.cntMn[i] = k

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
        self.tot[i] = self.tot[l] + self.tot[r]
        mn = self.mn; mn2 = self.mn2; cntMn = self.cntMn
        if mn[l] < mn[r]:
            mn[i] = mn[l]; cntMn[i] = cntMn[l]
            mn2[i] = mn2[l] if mn2[l] < mn[r] else mn[r]
        elif mn[l] > mn[r]:
            mn[i] = mn[r]; cntMn[i] = cntMn[r]
            mn2[i] = mn2[r] if mn2[r] < mn[l] else mn[l]
        else:
            mn[i] = mn[l]; cntMn[i] = cntMn[l] + cntMn[r]
            mn2[i] = mn2[l] if mn2[l] < mn2[r] else mn2[r]

    # every value under node i (sz of them) becomes v
    def _applyAssign(self, i, sz, v):
        self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = sz
        self.tot[i] = v * sz

    # chmax by v on node i, with v < mn2: only the copies of the min move
    def _applyChmax(self, i, sz, v):
        if self.mn[i] < v:
            self.tot[i] += (v - self.mn[i]) * self.cntMn[i]
            self.mn[i] = v

    # hand node i's pending changes to its children: all one value (an assign), else the add, then its own clamp
    def _push(self, i, tl, tr):
        self._kids(i)
        if tl == tr: return
        self._kids(i)
        tm = (tl + tr) // 2
        lsz = tm - tl + 1; rsz = tr - tm
        l = self.L[i]; r = self.R[i]
        if self.mn2[i] == POS_INF:
            v = self.mn[i]
            self._applyAssign(l, lsz, v); self._applyAssign(r, rsz, v)
            return
        self._applyChmax(l, lsz, self.mn[i]); self._applyChmax(r, rsz, self.mn[i])

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

    # amortized O(logU) -- a[i] = max(a[i], x) for i in [l, r]
    def rangeChmax(self, l, r, x):
        if l <= r: self._chmax(1, self.lo, self.hi, l, r, x)

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

    # amortized O(logU) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        if l <= r: self._assign(1, self.lo, self.hi, l, r, v)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return 0
        if ql <= tl and qr >= tr: return self.tot[i]
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        return self._sum(self.L[i], tl, tm, ql, qr) + self._sum(self.R[i], tm + 1, tr, ql, qr)

    # O(logU) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return 0 if (l > r) else self._sum(1, self.lo, self.hi, l, r)

    def _qmin(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return POS_INF
        if ql <= tl and qr >= tr: return self.mn[i]
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        a = self._qmin(self.L[i], tl, tm, ql, qr)
        b = self._qmin(self.R[i], tm + 1, tr, ql, qr)
        return a if a < b else b

    # O(logU) -- min of a[l..r]
    def rangeMin(self, l, r):
        return POS_INF if (l > r) else self._qmin(1, self.lo, self.hi, l, r)

    # O(logU) -- a[p]
    def pointGet(self, p):
        return self.rangeMin(p, p)

    # amortized O(logU) -- a[p] = v
    def pointAssign(self, p, v):
        self.rangeAssign(p, p, v)

    # amortized O(logU) -- a[i] += v
    def pointAdd(self, i, v):
        self.rangeAssign(i, i, self.pointGet(i) + v)

    # amortized O(logU) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        self.rangeChmax(i, i, v)

    # amortized O(logU) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        if v < self.pointGet(i): self.rangeAssign(i, i, v)

    # O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min)
    def leftmostLtX(self, l, r, x):
        F = self.mn
        res = self._firstPass(1, self.lo, self.hi, l, r, lambda i: F[i] < x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min)
    def leftmostLteX(self, l, r, x):
        F = self.mn
        res = self._firstPass(1, self.lo, self.hi, l, r, lambda i: F[i] <= x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min)
    def rightmostLtX(self, l, r, x):
        F = self.mn
        res = self._lastPass(1, self.lo, self.hi, l, r, lambda i: F[i] < x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min)
    def rightmostLteX(self, l, r, x):
        F = self.mn
        res = self._lastPass(1, self.lo, self.hi, l, r, lambda i: F[i] <= x) if l <= r else None
        return self.lo - 1 if res is None else res

    # the first index in [l, r] under node i whose value passes ok(node), or None: O(logU), since only one
    # node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    def _firstPass(self, i, tl, tr, l, r, ok):
        if r < tl or tr < l or not ok(i):
            return None
        if tl == tr:
            return tl
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        res = self._firstPass(self.L[i], tl, tm, l, r, ok)
        return res if res is not None else self._firstPass(self.R[i], tm + 1, tr, l, r, ok)

    # the last index in [l, r] under node i whose value passes ok(node), or None: O(logU), since only one
    # node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    def _lastPass(self, i, tl, tr, l, r, ok):
        if r < tl or tr < l or not ok(i):
            return None
        if tl == tr:
            return tl
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        res = self._lastPass(self.R[i], tm + 1, tr, l, r, ok)
        return res if res is not None else self._lastPass(self.L[i], tl, tm, l, r, ok)
