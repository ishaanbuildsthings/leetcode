# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeChmax rangeMin
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeAdd: log(U)
#   rangeChmax: log(U)
#   rangeMin: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mn[4*log(U)]
#   tags: lo[4*log(U)] add[4*log(U)]
#   other: links[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; Python: parallel lists

INF = float("inf")
NEG = float("-inf")


def _val(v, t):  # v after the tag t = (hi, lo, add): min(hi, max(lo, v + add))
    if t is None:
        return v
    v += t[2]
    if v < t[1]:
        v = t[1]
    return t[0] if v > t[0] else v


def _compose(o, t):  # tag o, then tag t; the maps compose into the same form
    if o is None:
        return t
    if t is None:
        return o
    h = min(t[0], max(t[1], o[0] + t[2]))
    return h, min(max(t[1], o[1] + t[2]), h), o[2] + t[2]


# Range add / chmax with range min queries, plus point ops, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# A tag is the map x -> min(hi, max(lo, x + add)), kept as (hi, lo, add); these maps compose into the same form,
# and each is monotone, so it sends a node's min / max straight to the new min / max.
# Updates push a node's tag into its children (creating them) before recursing past it; queries never push: they
# carry the ancestors' tags down and apply them to what they return, so they create no nodes.
# Sparse: parallel lists of nodes; node 0 is the shared all-zeros block (its sum, min and max are 0 at any
# length), node 1 is the root.


class SparseAddChmaxMinTree:
    __slots__ = ("lo", "hi", "L", "R", "mn", "tg")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.L = [0, 0]
        self.R = [0, 0]
        self.mn = [0, 0]
        self.tg = [None, None]  # pending tag of each node (None: none)

    def _kid(self, x, right):  # child of x, created as a block of zeros if missing
        kids = self.R if right else self.L
        y = kids[x]
        if not y:
            y = len(self.L)
            self.L.append(0)
            self.R.append(0)
            self.mn.append(0)
            self.tg.append(None)
            kids[x] = y
        return y

    # node x (k slots) takes tag t: its aggregate now, its children later
    def _apply(self, x, k, t):
        mn = self.mn
        mn[x] = _val(mn[x], t)
        self.tg[x] = _compose(self.tg[x], t)

    # move x's tag (x covers [a, b]) into its children, creating them
    def _push(self, x, a, b):
        t = self.tg[x]
        if t is not None:
            m = (a + b) // 2
            self._apply(self._kid(x, 0), m - a + 1, t)
            self._apply(self._kid(x, 1), b - m, t)
            self.tg[x] = None

    def _pull(self, x, k):
        mn = self.mn
        l, r = self.L[x], self.R[x]
        u, w = mn[l], mn[r]
        mn[x] = u if u < w else w

    def _update(self, x, a, b, l, r, t):
        if l <= a and b <= r:
            self._apply(x, b - a + 1, t)
            return
        self._push(x, a, b)
        m = (a + b) // 2
        if l <= m:
            self._update(self._kid(x, 0), a, m, l, r, t)
        if r > m:
            self._update(self._kid(x, 1), m + 1, b, l, r, t)
        self._pull(x, b - a + 1)

    # O(logU) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, (INF, NEG, v))

    # O(logU) -- a[i] = max(a[i], v) for i in [l, r]
    def rangeChmax(self, l, r, v):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, (INF, v, 0))

    # min of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with the ancestors' tag t on top
    def _qMin(self, x, a, b, l, r, t):
        if not x:
            return _val(0, t)
        mn = self.mn
        if l <= a and b <= r:
            return _val(mn[x], t)
        L, R = self.L, self.R
        d = _compose(self.tg[x], t)
        m = (a + b) // 2
        if r <= m:
            return self._qMin(L[x], a, m, l, r, d)
        if l > m:
            return self._qMin(R[x], m + 1, b, l, r, d)
        return min(self._qMin(L[x], a, m, l, r, d), self._qMin(R[x], m + 1, b, l, r, d))

    # O(logU) -- min of a[l..r]
    def rangeMin(self, l, r):
        return self._qMin(1, self.lo, self.hi, l, r, None)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._qMin(1, self.lo, self.hi, i, i, None)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        path = []
        x, a, b = 1, self.lo, self.hi
        while a < b:
            self._push(x, a, b)
            path.append((x, b - a + 1))
            m = (a + b) // 2
            if i <= m:
                x, b = self._kid(x, 0), m
            else:
                x, a = self._kid(x, 1), m + 1
        self.mn[x] = val
        for y, k in reversed(path):
            self._pull(y, k)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
