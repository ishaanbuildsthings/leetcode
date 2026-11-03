# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmax-rangeChmin-rangeMax-rangeMin-rangeSum-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/template.py
# @operations: getAll leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeChmin rangeMax rangeMin rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
# @data-structure-type: beats
# @complexities:
#   getAll: N
#   leftmostGtX: log(N)
#   leftmostGteX: log(N)
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   pointAdd: log(N) amortized
#   pointAssign: log(N) amortized
#   pointChmax: log(N) amortized
#   pointChmin: log(N) amortized
#   pointGet: log(N)
#   rangeAssign: log(N) amortized
#   rangeChmax: log(N) amortized
#   rangeChmin: log(N) amortized
#   rangeMax: log(N)
#   rangeMin: log(N)
#   rangeSum: log(N)
#   rightmostGtX: log(N)
#   rightmostGteX: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   build: N
# @memory:
#   layout: 4n-recursive
#   node: mx[4*N] mx2[4*N] cntMx[4*N] mn[4*N] mn2[4*N] cntMn[4*N] tot[4*N]
#   tags: none
#   other: none
#   note: no chmin / chmax / assign tags: a node's own mx / mn is its pending clamp, and a node whose values are all equal pushes that value as an assign

# Segment tree beats: range chmin (a[i] = min(a[i], x)) and chmax (a[i] = max(a[i], x)) and range assign, with range
# sums and the range max / min, plus point ops. All indices 0-based, ranges inclusive. How it works: a chmin only
# changes the max values of a node it covers, so a node keeps its max, its strict second max and how many copies of
# the max it has; a chmin x with mx2 < x < mx moves just those copies (the sum drops by (mx - x) * cntMx) and stops
# there, and only x <= mx2 has to go further down. a chmax is the same with the min: mn, mn2 and cntMn. A node's own
# mx / mn doubles as its pending clamp: push clamps each child to it, so there is no chmin / chmax tag. There is no
# assign tag either: when all of a node's values are equal (mn == mx), push hands that value to both children as an
# assign. Amortized O(log N) per update (beats: every extra descent removes a distinct value).

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
        self.mx[i] = v; self.mx2[i] = NEG_INF; self.cntMx[i] = sz
        self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = sz
        self.tot[i] = v * sz

    # chmin by v on node i, with mx2 < v: only the copies of the max move
    def _applyChmin(self, i, sz, v):
        if self.mn[i] >= v:
            self._applyAssign(i, sz, v); return
        if self.mx[i] > v:
            if self.mn2[i] == self.mx[i]: self.mn2[i] = v
            self.tot[i] -= (self.mx[i] - v) * self.cntMx[i]
            self.mx[i] = v

    # chmax by v on node i, with v < mn2: only the copies of the min move
    def _applyChmax(self, i, sz, v):
        if self.mx[i] <= v:
            self._applyAssign(i, sz, v); return
        if self.mn[i] < v:
            if self.mx2[i] == self.mn[i]: self.mx2[i] = v
            self.tot[i] += (v - self.mn[i]) * self.cntMn[i]
            self.mn[i] = v

    # hand node i's pending changes to its children: all one value (an assign), else the add, then its own clamp
    def _push(self, i, tl, tr):
        if tl == tr: return
        tm = (tl + tr) // 2
        lsz = tm - tl + 1; rsz = tr - tm
        l = 2 * i; r = l + 1
        if self.mn[i] == self.mx[i]:
            v = self.mx[i]
            self._applyAssign(l, lsz, v); self._applyAssign(r, rsz, v)
            return
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

    # amortized O(logN) -- a[i] = min(a[i], x) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmin(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # amortized O(logN) -- a[i] = max(a[i], x) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmax(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l <= r and self.n: self._chmax(1, 0, self.n - 1, l, r, x)

    def _assign(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr: return
        if ql <= tl and qr >= tr:
            self._applyAssign(i, tr - tl + 1, v); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._assign(2 * i, tl, tm, ql, qr, v)
        self._assign(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    # amortized O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l <= r and self.n: self._assign(1, 0, self.n - 1, l, r, v)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return 0
        if ql <= tl and qr >= tr: return self.tot[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        return self._sum(2 * i, tl, tm, ql, qr) + self._sum(2 * i + 1, tm + 1, tr, ql, qr)

    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return 0 if (l > r or not self.n) else self._sum(1, 0, self.n - 1, l, r)

    def _qmax(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return NEG_INF
        if ql <= tl and qr >= tr: return self.mx[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._qmax(2 * i, tl, tm, ql, qr)
        b = self._qmax(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a > b else b

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return NEG_INF if (l > r or not self.n) else self._qmax(1, 0, self.n - 1, l, r)

    def _qmin(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return POS_INF
        if ql <= tl and qr >= tr: return self.mn[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._qmin(2 * i, tl, tm, ql, qr)
        b = self._qmin(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a < b else b

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return POS_INF if (l > r or not self.n) else self._qmin(1, 0, self.n - 1, l, r)

    # O(logN) -- a[p]; needs 0 <= p < n, else IndexError
    def pointGet(self, p):
        if not 0 <= p < self.n:
            raise IndexError(f"pointGet: needs 0 <= p < n, got p = {p}, n = {self.n}")
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

    # amortized O(logN) -- a[p] = v; needs 0 <= p < n, else IndexError
    def pointAssign(self, p, v):
        if not 0 <= p < self.n:
            raise IndexError(f"pointAssign: needs 0 <= p < n, got p = {p}, n = {self.n}")
        self.rangeAssign(p, p, v)

    # amortized O(logN) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAssign(i, i, self.pointGet(i) + v)

    # amortized O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeChmax(i, i, v)

    # amortized O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeChmin(i, i, v)

    # O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mx
        return self._firstPass(1, 0, self.n - 1, l, r, lambda i: F[i] > x) if l <= r and self.n else -1

    # O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mx
        return self._firstPass(1, 0, self.n - 1, l, r, lambda i: F[i] >= x) if l <= r and self.n else -1

    # O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mn
        return self._firstPass(1, 0, self.n - 1, l, r, lambda i: F[i] < x) if l <= r and self.n else -1

    # O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mn
        return self._firstPass(1, 0, self.n - 1, l, r, lambda i: F[i] <= x) if l <= r and self.n else -1

    # O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mx
        return self._lastPass(1, 0, self.n - 1, l, r, lambda i: F[i] > x) if l <= r and self.n else -1

    # O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mx
        return self._lastPass(1, 0, self.n - 1, l, r, lambda i: F[i] >= x) if l <= r and self.n else -1

    # O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mn
        return self._lastPass(1, 0, self.n - 1, l, r, lambda i: F[i] < x) if l <= r and self.n else -1

    # O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mn
        return self._lastPass(1, 0, self.n - 1, l, r, lambda i: F[i] <= x) if l <= r and self.n else -1

    # the first index in [l, r] under node i whose value passes ok(node), or -1: O(logN), since only one
    # node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    def _firstPass(self, i, tl, tr, l, r, ok):
        if r < tl or tr < l or not ok(i):
            return -1
        if tl == tr:
            return tl
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        res = self._firstPass(2 * i, tl, tm, l, r, ok)
        return res if res != -1 else self._firstPass(2 * i + 1, tm + 1, tr, l, r, ok)

    # the last index in [l, r] under node i whose value passes ok(node), or -1: O(logN), since only one
    # node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    def _lastPass(self, i, tl, tr, l, r, ok):
        if r < tl or tr < l or not ok(i):
            return -1
        if tl == tr:
            return tl
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        res = self._lastPass(2 * i + 1, tm + 1, tr, l, r, ok)
        return res if res != -1 else self._lastPass(2 * i, tl, tm, l, r, ok)
