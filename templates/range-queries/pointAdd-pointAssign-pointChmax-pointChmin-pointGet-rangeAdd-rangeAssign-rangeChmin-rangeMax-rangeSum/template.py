# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmin-rangeMax-rangeSum/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmin rangeMax rangeSum
# @data-structure-type: beats
# @complexities:
#   getAll: N
#   pointAdd: log^2(N) amortized
#   pointAssign: log^2(N) amortized
#   pointChmax: log^2(N) amortized
#   pointChmin: log^2(N) amortized
#   pointGet: log(N)
#   rangeAdd: log^2(N) amortized
#   rangeAssign: log^2(N) amortized
#   rangeChmin: log^2(N) amortized
#   rangeMax: log(N)
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: 4n-recursive
#   node: mx[4*N] mx2[4*N] cntMx[4*N] tot[4*N]
#   tags: addTag[4*N]
#   other: none
#   note: no chmin / chmax / assign tags: a node's own mx is its pending clamp, and a node whose values are all equal pushes that value as an assign

# Segment tree beats: range chmin (a[i] = min(a[i], x)), range add and range assign, with range sums and the range
# max, plus point ops. All indices 0-based, ranges inclusive. How it works: a chmin only changes the max values of a
# node it covers, so a node keeps its max, its strict second max and how many copies of the max it has; a chmin x with
# mx2 < x < mx moves just those copies (the sum drops by (mx - x) * cntMx) and stops there, and only x <= mx2 has to
# go further down. A node's own mx doubles as its pending clamp: push clamps each child to it, so there is no chmin /
# chmax tag. There is no assign tag either: when all of a node's values are equal (no second max), push hands that
# value to both children as an assign. An add shifts everything a node keeps and goes in the one add tag. Amortized
# O(log^2 N) per update with range add, O(log N) without it (beats: every extra descent removes a distinct value).

NEG_INF = float('-inf')
POS_INF = float('inf')


class ChminChmaxBeats:
    # O(N)
    def __init__(self, arr):
        self.n = n = len(arr)
        size = 4 * max(1, n)
        self.mx = [0] * size
        self.mx2 = [NEG_INF] * size
        self.cntMx = [0] * size
        self.tot = [0] * size
        self.addTag = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        if tl == tr:
            v = arr[tl]
            self.mx[i] = v; self.mx2[i] = NEG_INF; self.cntMx[i] = 1
            self.tot[i] = v; self.addTag[i] = 0
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        l = 2 * i; r = l + 1
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
        if tl == tr: return
        tm = (tl + tr) // 2
        lsz = tm - tl + 1; rsz = tr - tm
        l = 2 * i; r = l + 1
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
        tm = (tl + tr) // 2
        self._chmin(2 * i, tl, tm, ql, qr, x)
        self._chmin(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    # amortized O(log^2 N) -- a[i] = min(a[i], x) for i in [l, r]
    def rangeChmin(self, l, r, x):
        if l <= r and self.n: self._chmin(1, 0, self.n - 1, l, r, x)

    def _add(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr: return
        if ql <= tl and qr >= tr:
            self._applyAdd(i, tr - tl + 1, v); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._add(2 * i, tl, tm, ql, qr, v)
        self._add(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    # amortized O(log^2 N) -- a[i] += v for i in [l, r]
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

    # amortized O(log^2 N) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        if l <= r and self.n: self._assign(1, 0, self.n - 1, l, r, v)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return 0
        if ql <= tl and qr >= tr: return self.tot[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        return self._sum(2 * i, tl, tm, ql, qr) + self._sum(2 * i + 1, tm + 1, tr, ql, qr)

    # O(logN) -- a[l] + ... + a[r]
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

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        return NEG_INF if (l > r or not self.n) else self._qmax(1, 0, self.n - 1, l, r)

    # O(logN) -- a[p]
    def pointGet(self, p):
        return self.rangeMax(p, p)

    def _getAllRec(self, i, tl, tr, out):
        if tl == tr:
            out.append(self.mx[i])
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._getAllRec(2 * i, tl, tm, out)
        self._getAllRec(2 * i + 1, tm + 1, tr, out)

    # O(N) -- the whole array: one DFS that pushes every tag down and reads the leaves left to right
    def getAll(self):
        out = []
        if self.n:
            self._getAllRec(1, 0, self.n - 1, out)
        return out

    # amortized O(log^2 N) -- a[p] = v
    def pointAssign(self, p, v):
        self.rangeAssign(p, p, v)

    # amortized O(log^2 N) -- a[i] += v
    def pointAdd(self, i, v):
        self.rangeAdd(i, i, v)

    # amortized O(log^2 N) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        if v > self.pointGet(i): self.rangeAssign(i, i, v)

    # amortized O(log^2 N) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        self.rangeChmin(i, i, v)
