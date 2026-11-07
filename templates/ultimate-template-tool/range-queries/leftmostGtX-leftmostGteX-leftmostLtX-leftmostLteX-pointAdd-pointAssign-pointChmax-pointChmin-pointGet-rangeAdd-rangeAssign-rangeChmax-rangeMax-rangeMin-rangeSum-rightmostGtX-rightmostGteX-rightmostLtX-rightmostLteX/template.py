# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmax-rangeMax-rangeMin-rangeSum-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/template.py
# @operations: getAll leftmostGtX leftmostGteX leftmostLtX leftmostLteX maxAll minAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeMax rangeMin rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX sumAll
# @data-structure-type: beats
# @complexities:
#   getAll: N
#   leftmostGtX: log(N)
#   leftmostGteX: log(N)
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   pointAdd: log^2(N) amortized
#   pointAssign: log^2(N) amortized
#   pointChmax: log^2(N) amortized
#   pointChmin: log^2(N) amortized
#   pointGet: log(N)
#   rangeAdd: log^2(N) amortized
#   rangeAssign: log^2(N) amortized
#   rangeChmax: log^2(N) amortized
#   rangeMax: log(N)
#   rangeMin: log(N)
#   rangeSum: log(N)
#   rightmostGtX: log(N)
#   rightmostGteX: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   sumAll: log(N)
#   minAll: log(N)
#   maxAll: log(N)
#   build: N
# @memory:
#   layout: 4n-recursive
#   node: mx[4*N] mn[4*N] mn2[4*N] cntMn[4*N] tot[4*N]
#   tags: addTag[4*N]
#   other: none
#   note: no chmin / chmax / assign tags: a node's own mn is its pending clamp, and a node whose values are all equal pushes that value as an assign

# Segment tree beats: range chmax (a[i] = max(a[i], x)), range add and range assign, with range sums and the range max
# / min, plus point ops. All indices 0-based, ranges inclusive. How it works: a chmax only changes the min values of a
# node it covers, so a node keeps its min, its strict second min and how many copies of the min it has; a chmax x with
# mn < x < mn2 moves just those copies (the sum rises by (x - mn) * cntMn) and stops there, and only x >= mn2 has to
# go further down. A node's own mn doubles as its pending clamp: push clamps each child to it, so there is no chmin /
# chmax tag. There is no assign tag either: when all of a node's values are equal (no second min), push hands that
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
        self.mn = [0] * size
        self.mn2 = [POS_INF] * size
        self.cntMn = [0] * size
        self.tot = [0] * size
        self.addTag = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        if tl == tr:
            v = arr[tl]
            self.mx[i] = v
            self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = 1
            self.tot[i] = v; self.addTag[i] = 0
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        l = 2 * i; r = l + 1
        self.tot[i] = self.tot[l] + self.tot[r]
        a = self.mx[l]; b = self.mx[r]
        self.mx[i] = a if a > b else b
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
        self.addTag[i] = 0

    # every value under node i (sz of them) becomes v
    def _applyAssign(self, i, sz, v):
        self.mx[i] = v
        self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = sz
        self.tot[i] = v * sz; self.addTag[i] = 0

    # every value under node i gains v
    def _applyAdd(self, i, sz, v):
        if self.mn2[i] == POS_INF:
            self._applyAssign(i, sz, self.mx[i] + v); return
        self.mx[i] += v
        self.mn[i] += v
        if self.mn2[i] != POS_INF: self.mn2[i] += v
        self.tot[i] += sz * v
        self.addTag[i] += v

    # chmax by v on node i, with v < mn2: only the copies of the min move
    def _applyChmax(self, i, sz, v):
        if self.mn[i] < v:
            self.tot[i] += (v - self.mn[i]) * self.cntMn[i]
            self.mn[i] = v
            if self.mx[i] < v: self.mx[i] = v

    # hand node i's pending changes to its children: all one value (an assign), else the add, then its own clamp
    def _push(self, i, tl, tr):
        if tl == tr: return
        tm = (tl + tr) // 2
        lsz = tm - tl + 1; rsz = tr - tm
        l = 2 * i; r = l + 1
        if self.mn2[i] == POS_INF:
            v = self.mx[i]
            self._applyAssign(l, lsz, v); self._applyAssign(r, rsz, v)
            return
        a = self.addTag[i]
        if a:
            self._applyAdd(l, lsz, a); self._applyAdd(r, rsz, a)
            self.addTag[i] = 0
        self._applyChmax(l, lsz, self.mn[i]); self._applyChmax(r, rsz, self.mn[i])

    def _chmax(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x <= self.mn[i]: return
        if ql <= tl and qr >= tr and x < self.mn2[i]:
            self._applyChmax(i, tr - tl + 1, x); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._chmax(2 * i, tl, tm, ql, qr, x)
        self._chmax(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    # amortized O(log^2 N) -- a[i] = max(a[i], x) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmax(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # amortized O(log^2 N) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # amortized O(log^2 N) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
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

    # amortized O(log^2 N) -- a[p] = v; needs 0 <= p < n, else IndexError
    def pointAssign(self, p, v):
        if not 0 <= p < self.n:
            raise IndexError(f"pointAssign: needs 0 <= p < n, got p = {p}, n = {self.n}")
        self.rangeAssign(p, p, v)

    # amortized O(log^2 N) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAdd(i, i, v)

    # amortized O(log^2 N) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeChmax(i, i, v)

    # amortized O(log^2 N) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if v < self.pointGet(i): self.rangeAssign(i, i, v)

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

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):

    # O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):

    # O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.n < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.n - 1)
        if self.n < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.n - 1)
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)
        if r < tl or tr < l or not ok(i):
            return -1
        if tl == tr:
            return tl
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        res = self._lastPass(2 * i + 1, tm + 1, tr, l, r, ok)
        return res if res != -1 else self._lastPass(2 * i, tl, tm, l, r, ok)
