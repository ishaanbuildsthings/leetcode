# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostGtX-leftmostGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmin-rangeMax-rangeSum-rightmostGtX-rightmostGteX/sparse.py
# @operations: leftmostGtX leftmostGteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmin rangeMax rangeSum rightmostGtX rightmostGteX
# @data-structure-type: beats
# @complexities:
#   leftmostGtX: log(U)
#   leftmostGteX: log(U)
#   pointAdd: log(U)*log(U) amortized
#   pointAssign: log(U)*log(U) amortized
#   pointChmax: log(U)*log(U) amortized
#   pointChmin: log(U)*log(U) amortized
#   pointGet: log(U)
#   rangeAdd: log(U)*log(U) amortized
#   rangeAssign: log(U)*log(U) amortized
#   rangeChmin: log(U)*log(U) amortized
#   rangeMax: log(U)
#   rangeSum: log(U)
#   rightmostGtX: log(U)
#   rightmostGteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mx[4*log(U)] mx2[4*log(U)] cntMx[4*log(U)] tot[4*log(U)]
#   tags: addTag[4*log(U)]
#   other: none
#   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. Per-node lists that grow

# Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
# is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
# right before anything descends past a node or pushes its tags. Otherwise the beats logic below is the
# dense tree's, with children in L / R instead of at 2i / 2i + 1.

# Segment tree beats: range chmin (a[i] = min(a[i], x)), range add and range assign, with range sums and the range
# max, plus point ops. All indices 0-based, ranges inclusive. How it works: a chmin only changes the max values of a
# node it covers, so a node keeps its max, its strict second max and how many copies of the max it has; a chmin x with
# mx2 < x < mx moves just those copies (the sum drops by (mx - x) * cntMx) and stops there, and only x <= mx2 has to
# go further down. A node's own mx doubles as its pending clamp: push clamps each child to it, so there is no chmin /
# chmax tag. There is no assign tag either: when all of a node's values are equal (no second max), push hands that
# value to both children as an assign. An add shifts everything a node keeps and goes in the one add tag. Amortized
# O(logU * logU) per update with range add, O(log U) without it (beats: every extra descent removes a distinct value).

NEG_INF = float('-inf')
POS_INF = float('inf')


class SparseChminChmaxBeats:
    # O(N)
    # O(1) -- all zeros over [lo, hi]; any range of integers works
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        # node 0 is unused; node 1 is the root, one block of hi - lo + 1 zeros
        self.L, self.R, self.ln = [0, 0], [0, 0], [0, 0]
        self.mx = [0] * 2
        self.mx2 = [NEG_INF] * 2
        self.cntMx = [0] * 2
        self.tot = [0] * 2
        self.addTag = [0] * 2
        self._zero(1, hi - lo + 1)

    # node i becomes a block of k zeros (its defaults, plus every count = k)
    def _zero(self, i, k):
        self.ln[i] = k
        self.cntMx[i] = k

    # a fresh node: a block of k zeros
    def _node(self, k):
        j = len(self.L)
        self.L.append(0)
        self.R.append(0)
        self.ln.append(0)
        self.mx.append(0)
        self.mx2.append(NEG_INF)
        self.cntMx.append(0)
        self.tot.append(0)
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
        self.tot[i] = self.tot[l] + self.tot[r]
        mx = self.mx; mx2 = self.mx2; cntMx = self.cntMx
        if mx[l] > mx[r]:
            mx[i] = mx[l]; cntMx[i] = cntMx[l]
            mx2[i] = mx2[l] if mx2[l] > mx[r] else mx[r]
        elif mx[l] < mx[r]:
            mx[i] = mx[r]; cntMx[i] = cntMx[r]
            mx2[i] = mx2[r] if mx2[r] > mx[l] else mx[l]
        else:
            mx[i] = mx[l]; cntMx[i] = cntMx[l] + cntMx[r]
            mx2[i] = mx2[l] if mx2[l] > mx2[r] else mx2[r]
        self.addTag[i] = 0

    # every value under node i (sz of them) becomes v
    def _applyAssign(self, i, sz, v):
        self.mx[i] = v; self.mx2[i] = NEG_INF; self.cntMx[i] = sz
        self.tot[i] = v * sz; self.addTag[i] = 0

    # every value under node i gains v
    def _applyAdd(self, i, sz, v):
        if self.mx2[i] == NEG_INF:
            self._applyAssign(i, sz, self.mx[i] + v); return
        self.mx[i] += v
        if self.mx2[i] != NEG_INF: self.mx2[i] += v
        self.tot[i] += sz * v
        self.addTag[i] += v

    # chmin by v on node i, with mx2 < v: only the copies of the max move
    def _applyChmin(self, i, sz, v):
        if self.mx[i] > v:
            self.tot[i] -= (self.mx[i] - v) * self.cntMx[i]
            self.mx[i] = v

    # hand node i's pending changes to its children: all one value (an assign), else the add, then its own clamp
    def _push(self, i, tl, tr):
        self._kids(i)
        if tl == tr: return
        self._kids(i)
        tm = (tl + tr) // 2
        lsz = tm - tl + 1; rsz = tr - tm
        l = self.L[i]; r = self.R[i]
        if self.mx2[i] == NEG_INF:
            v = self.mx[i]
            self._applyAssign(l, lsz, v); self._applyAssign(r, rsz, v)
            return
        a = self.addTag[i]
        if a:
            self._applyAdd(l, lsz, a); self._applyAdd(r, rsz, a)
            self.addTag[i] = 0
        self._applyChmin(l, lsz, self.mx[i]); self._applyChmin(r, rsz, self.mx[i])

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

    # amortized O(logU * logU) -- a[i] = min(a[i], x) for i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def rangeChmin(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeChmin: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if l <= r: self._chmin(1, self.lo, self.hi, l, r, x)

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

    # amortized O(logU * logU) -- a[i] += v for i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def rangeAdd(self, l, r, v):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeAdd: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
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

    # amortized O(logU * logU) -- a[i] = v for i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def rangeAssign(self, l, r, v):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeAssign: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if l <= r: self._assign(1, self.lo, self.hi, l, r, v)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return 0
        if ql <= tl and qr >= tr: return self.tot[i]
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        return self._sum(self.L[i], tl, tm, ql, qr) + self._sum(self.R[i], tm + 1, tr, ql, qr)

    # O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeSum(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
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

    # O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMax(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeMax: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return NEG_INF if (l > r) else self._qmax(1, self.lo, self.hi, l, r)

    # O(logU) -- a[p]; needs lo <= p <= hi, else IndexError
    def pointGet(self, p):
        if not self.lo <= p <= self.hi:
            raise IndexError(f"pointGet: needs lo <= p <= hi, got p = {p}")
        return self.rangeMax(p, p)

    # amortized O(logU * logU) -- a[p] = v; needs lo <= p <= hi, else IndexError
    def pointAssign(self, p, v):
        if not self.lo <= p <= self.hi:
            raise IndexError(f"pointAssign: needs lo <= p <= hi, got p = {p}")
        self.rangeAssign(p, p, v)

    # amortized O(logU * logU) -- a[i] += v; needs lo <= i <= hi, else IndexError
    def pointAdd(self, i, v):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAdd: needs lo <= i <= hi, got i = {i}")
        self.rangeAdd(i, i, v)

    # amortized O(logU * logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else IndexError
    def pointChmax(self, i, v):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmax: needs lo <= i <= hi, got i = {i}")
        if v > self.pointGet(i): self.rangeAssign(i, i, v)

    # amortized O(logU * logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else IndexError
    def pointChmin(self, i, v):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmin: needs lo <= i <= hi, got i = {i}")
        self.rangeChmin(i, i, v)

    # O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"leftmostGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mx
        res = self._firstPass(1, self.lo, self.hi, l, r, lambda i: F[i] > x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"leftmostGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mx
        res = self._firstPass(1, self.lo, self.hi, l, r, lambda i: F[i] >= x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rightmostGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mx
        res = self._lastPass(1, self.lo, self.hi, l, r, lambda i: F[i] > x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rightmostGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mx
        res = self._lastPass(1, self.lo, self.hi, l, r, lambda i: F[i] >= x) if l <= r else None
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
