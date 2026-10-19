# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeMax rangeMin
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeAssign: log(N)
#   rangeChmax: log(N)
#   rangeChmin: log(N)
#   rangeMax: log(N)
#   rangeMin: log(N)
#   build: N
# @memory:
#   layout: pow2-iterative
#   node: mn[4*N] mx[4*N]
#   tags: A[2*N] B[2*N] C[2*N]
#   other: none
#   note: one clamp tag per node: x -> min(A, max(B, x + C))
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/rangeChmin-Chmax-Add-Assign-Min-Max-PointSet-NO-BEATS.py

# TEMPLATE BY https://github.com/agrawalishaan

# ========================
# COMPLEXITIES

# O(n) build
# LazyClamp_PERFORMANT(arr)

# O(logN):  rangeChmin(l, r, x)    -- a[i] = min(a[i], x)
# O(logN):  rangeChmax(l, r, x)    -- a[i] = max(a[i], x)
# O(logN):  rangeAdd(l, r, x)      -- a[i] += x
# O(logN):  rangeAssign(l, r, x)   -- a[i] = x
# O(logN):  pointAssign(pos, newVal)

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
    """Iterative lazy tree over a power-of-two layout. An update pushes every tag on its two boundary
    root-to-leaf paths, tags the O(log N) covering nodes, then recomputes the boundary paths bottom-up."""
    __slots__ = ("n", "size", "H", "mn", "mx", "A", "B", "C")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        size, H = 1, 0
        while size < max(n, 1):
            size <<= 1
            H += 1
        self.size, self.H = size, H
        mn = self.mn = [POS_INF] * (2 * size)  # padding leaves never win a min / max
        mx = self.mx = [NEG_INF] * (2 * size)
        for i, v in enumerate(arr):
            mn[size + i] = mx[size + i] = v
        for x in range(size - 1, 0, -1):
            mn[x] = mn[2 * x] if mn[2 * x] < mn[2 * x + 1] else mn[2 * x + 1]
            mx[x] = mx[2 * x] if mx[2 * x] > mx[2 * x + 1] else mx[2 * x + 1]
        self.A = [POS_INF] * size  # tags live on internal nodes only
        self.B = [NEG_INF] * size
        self.C = [0] * size

    @staticmethod
    def _eval(x, a, b, c):
        v = x + c
        if v < b:
            v = b
        if v > a:
            v = a
        return v

    # a clamp is monotone, so it maps the node's min to the new min and its max to the new max
    def _apply(self, i, a, b, c):
        self.mn[i] = self._eval(self.mn[i], a, b, c)
        self.mx[i] = self._eval(self.mx[i], a, b, c)
        if i < self.size:
            sA = self.A[i] + c
            sB = self.B[i] + c
            nA = sA if sA > b else b
            if nA > a:
                nA = a
            nB = sB if sB > b else b
            if nB > nA:
                nB = nA
            self.A[i] = nA
            self.B[i] = nB
            self.C[i] += c

    def _push(self, i):
        a, b, c = self.A[i], self.B[i], self.C[i]
        if a == POS_INF and b == NEG_INF and c == 0:
            return
        self._apply(2 * i, a, b, c)
        self._apply(2 * i + 1, a, b, c)
        self.A[i] = POS_INF
        self.B[i] = NEG_INF
        self.C[i] = 0

    def _pushToRoot(self, p):
        for s in range(self.H, 0, -1):
            self._push(p >> s)

    # a node tagged during this update keeps its own clamp on top of its children
    def _recomputeToRoot(self, p):
        mn, mx, A, B, C, ev = self.mn, self.mx, self.A, self.B, self.C, self._eval
        p >>= 1
        while p:
            lo = mn[2 * p] if mn[2 * p] < mn[2 * p + 1] else mn[2 * p + 1]
            hi = mx[2 * p] if mx[2 * p] > mx[2 * p + 1] else mx[2 * p + 1]
            if A[p] == POS_INF and B[p] == NEG_INF and C[p] == 0:
                mn[p], mx[p] = lo, hi
            else:
                mn[p], mx[p] = ev(lo, A[p], B[p], C[p]), ev(hi, A[p], B[p], C[p])
            p >>= 1

    def _upd(self, l, r, a, b, c):
        if l > r:
            return
        l0, r0 = l + self.size, r + self.size
        self._pushToRoot(l0)
        self._pushToRoot(r0)
        lo, hi = l0, r0 + 1
        while lo < hi:
            if lo & 1:
                self._apply(lo, a, b, c)
                lo += 1
            if hi & 1:
                hi -= 1
                self._apply(hi, a, b, c)
            lo >>= 1
            hi >>= 1
        self._recomputeToRoot(l0)
        self._recomputeToRoot(r0)

    # fold of min (or max) over the canonical nodes of [l, r], after pushing the boundary paths
    def _query(self, l, r, arr, isMin):
        l += self.size
        r += self.size
        self._pushToRoot(l)
        self._pushToRoot(r)
        res = POS_INF if isMin else NEG_INF
        r += 1
        while l < r:
            if l & 1:
                v = arr[l]
                if (v < res) if isMin else (v > res):
                    res = v
                l += 1
            if r & 1:
                r -= 1
                v = arr[r]
                if (v < res) if isMin else (v > res):
                    res = v
            l >>= 1
            r >>= 1
        return res

    ################ PUBLIC METHODS START HERE ################

    # O(log n) -- a[i] = min(a[i], x) for i in l...r
    def rangeChmin(self, l, r, x):
        self._upd(l, r, x, NEG_INF, 0)

    # O(log n) -- a[i] = max(a[i], x) for i in l...r
    def rangeChmax(self, l, r, x):
        self._upd(l, r, POS_INF, x, 0)

    # O(log n) -- a[i] += x for i in l...r
    def rangeAdd(self, l, r, x):
        self._upd(l, r, POS_INF, NEG_INF, x)

    # O(log n) -- a[i] = x for i in l...r
    def rangeAssign(self, l, r, x):
        self._upd(l, r, x, x, 0)

    # O(log n) -- a[i] = x
    def pointAssign(self, p, x):
        self._upd(p, p, x, x, 0)

    # O(log n) -- min of l...r
    def rangeMin(self, l, r):
        return POS_INF if l > r else self._query(l, r, self.mn, True)

    # O(log n) -- max of l...r
    def rangeMax(self, l, r):
        return NEG_INF if l > r else self._query(l, r, self.mx, False)

    # O(log n) -- a[i]
    def pointGet(self, p):
        p += self.size
        self._pushToRoot(p)
        return self.mn[p]

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        self._upd(i, i, POS_INF, val, 0)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        self._upd(i, i, val, NEG_INF, 0)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self._upd(i, i, POS_INF, NEG_INF, delta)
