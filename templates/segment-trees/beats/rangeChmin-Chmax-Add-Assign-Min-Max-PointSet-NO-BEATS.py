# TEMPLATE BY https://github.com/agrawalishaan

# ========================
# COMPLEXITIES

# O(n) build
# LazyClamp_PERFORMANT(arr)

# O(logN):  rangeChmin(l, r, x)    -- a[i] = min(a[i], x)
# O(logN):  rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
# O(logN):  rangeAdd(l, r, x)      -- a[i] += x
# O(logN):  rangeAssign(l, r, x)   -- a[i] = x
# O(logN):  pointSet(pos, newVal)

# O(logN):  rangeMin(l, r)
# O(logN):  rangeMax(l, r)
# O(logN):  pointGet(pos)
# O(n) space

# NOT BEATS -- a completely normal lazy segment tree, NOT amortized, worst case logN per op.
# NO rangeSum. That is the whole catch, and it is why segment tree beats has to exist.

# ========================
"""
WHY THIS WORKS (and why there is no sum)

Any sequence of chmin / chmax / add collapses into a SINGLE closed form:

    f(x) = min(a, max(b, x + c))

three numbers, so it is an ordinary lazy tag. Reading it inside out: shift by c, floor at b, cap at
a. That is add-BEFORE-clamp, but it is not a restriction on the order you call things -- an add
arriving AFTER a clamp just gets pushed through, since adding v to min(a, max(b, x+c)) gives
min(a+v, max(b+v, x+c+v)), so all three constants shift and the shape survives.

Composing a new g = (a, b, c) on top of a stored f = (A, B, C):
    newA = min(a, max(b, A + c))
    newB = max(b, B + c)
    newC = C + c
    if (newA < newB) newB = newA;   // the window collapsed, f is now the constant newA

The individual ops are just special cases:
    add v     -> (+INF, -INF, v)
    chmin v   -> (v,    -INF, 0)
    chmax v   -> (+INF, v,    0)
    assign v  -> (v,    v,    0)

min and max survive because f is monotone non-decreasing, so the smallest element is still the
smallest after the shift and both clamps. You just run the node's stored mn and mx through f.

SUM DOES NOT SURVIVE. A node holding [1, 9] and a node holding [5, 5] both have sum 10, and
clamping both at 5 gives 6 and 10. Same sum in, same operation, different sum out -- so there is no
function of (sum, size, tag) that gives the answer. The result genuinely depends on the individual
values, which a node does not store. THAT is the dividing line: if you need sum, you need beats
(and you pay a second log for the add).

Classic problem: IOI 2014 Wall.
"""

# ========================



NEG_INF = float('-inf')
POS_INF = float('inf')


class LazyClamp_PERFORMANT:
    def __init__(self, arr):
        self.n = n = len(arr)
        size = 4 * max(1, n)
        self.mn = [0] * size
        self.mx = [0] * size
        self.A = [POS_INF] * size
        self.B = [NEG_INF] * size
        self.C = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    @staticmethod
    def _eval(x, a, b, c):
        v = x + c
        if v < b:
            v = b
        if v > a:
            v = a
        return v

    def _build(self, i, tl, tr, arr):
        self.A[i] = POS_INF; self.B[i] = NEG_INF; self.C[i] = 0
        if tl == tr:
            self.mn[i] = self.mx[i] = arr[tl]
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        l = 2 * i; r = l + 1
        self.mn[i] = self.mn[l] if self.mn[l] < self.mn[r] else self.mn[r]
        self.mx[i] = self.mx[l] if self.mx[l] > self.mx[r] else self.mx[r]
        self.A[i] = POS_INF; self.B[i] = NEG_INF; self.C[i] = 0

    def _apply(self, i, a, b, c):
        self.mn[i] = self._eval(self.mn[i], a, b, c)
        self.mx[i] = self._eval(self.mx[i], a, b, c)
        sA = self.A[i] + c
        sB = self.B[i] + c
        nA = sA if sA > b else b
        if nA > a:
            nA = a
        nB = sB if sB > b else b
        self.C[i] += c
        if nA < nB:
            nB = nA
        self.A[i] = nA; self.B[i] = nB

    def _push(self, i, tl, tr):
        if tl == tr:
            return
        a = self.A[i]; b = self.B[i]; c = self.C[i]
        if a == POS_INF and b == NEG_INF and c == 0:
            return
        self._apply(2 * i, a, b, c)
        self._apply(2 * i + 1, a, b, c)
        self.A[i] = POS_INF; self.B[i] = NEG_INF; self.C[i] = 0

    def _upd(self, i, tl, tr, ql, qr, a, b, c):
        if qr < tl or ql > tr:
            return
        if ql <= tl and qr >= tr:
            self._apply(i, a, b, c)
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._upd(2 * i, tl, tm, ql, qr, a, b, c)
        self._upd(2 * i + 1, tm + 1, tr, ql, qr, a, b, c)
        self._pull(i)

    def rangeChmin(self, l, r, x):
        if l <= r and self.n:
            self._upd(1, 0, self.n - 1, l, r, x, NEG_INF, 0)

    def rangeChmax(self, l, r, x):
        if l <= r and self.n:
            self._upd(1, 0, self.n - 1, l, r, POS_INF, x, 0)

    def rangeAdd(self, l, r, x):
        if l <= r and self.n:
            self._upd(1, 0, self.n - 1, l, r, POS_INF, NEG_INF, x)

    def rangeAssign(self, l, r, x):
        if l <= r and self.n:
            self._upd(1, 0, self.n - 1, l, r, x, x, 0)

    def pointSet(self, p, x):
        self.rangeAssign(p, p, x)

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

    def pointGet(self, p):
        return self.rangeMin(p, p)