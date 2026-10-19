# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeMax rangeSum
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeAdd: log(U)
#   rangeAssign: log(U)
#   rangeMax: log(U)
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[4*log(U)] mx[4*log(U)]
#   tags: add[4*log(U)] asg[4*log(U)] hasAsg[4*log(U)]
#   other: links[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; Python: parallel lists


def _val(v, t):  # one slot after the tag t = (assigned value or None, add)
    if t is None:
        return v
    return t[0] if t[0] is not None else v + t[1]


def _sum(s, k, t):  # the sum s of k slots after the tag t
    if t is None:
        return s
    return t[0] * k if t[0] is not None else s + t[1] * k


def _compose(o, t):  # tag o, then tag t (an add on an assign shifts the assigned value)
    if o is None:
        return t
    if t is None or t[0] is not None:
        return o if t is None else t
    if o[0] is not None:
        return o[0] + t[1], 0
    return None, o[1] + t[1]


# Range add / assign with range sum / max queries, plus point ops, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# A tag is (assigned value or None, add): an assign, or an add (an add on an assigned node shifts the value).
# Updates push a node's tag into its children (creating them) before recursing past it; queries never push: they
# carry the ancestors' tags down and apply them to what they return, so they create no nodes.
# Sparse: parallel lists of nodes; node 0 is the shared all-zeros block (its sum, min and max are 0 at any
# length), node 1 is the root.


class SparseAddAssignSumMaxTree:
    __slots__ = ("lo", "hi", "L", "R", "sm", "mx", "tg")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.L = [0, 0]
        self.R = [0, 0]
        self.sm = [0, 0]
        self.mx = [0, 0]
        self.tg = [None, None]  # pending tag of each node (None: none)

    def _kid(self, x, right):  # child of x, created as a block of zeros if missing
        kids = self.R if right else self.L
        y = kids[x]
        if not y:
            y = len(self.L)
            self.L.append(0)
            self.R.append(0)
            self.sm.append(0)
            self.mx.append(0)
            self.tg.append(None)
            kids[x] = y
        return y

    # node x (k slots) takes tag t: its aggregate now, its children later
    def _apply(self, x, k, t):
        sm, mx = self.sm, self.mx
        sm[x] = _sum(sm[x], k, t)
        mx[x] = _val(mx[x], t)
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
        sm, mx = self.sm, self.mx
        l, r = self.L[x], self.R[x]
        v = sm[l] + sm[r]
        sm[x] = v
        u, w = mx[l], mx[r]
        mx[x] = u if u > w else w

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
            self._update(1, self.lo, self.hi, l, r, (None, v))

    # O(logU) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, (v, 0))

    # sum of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with the ancestors' tag t on top
    def _qSum(self, x, a, b, l, r, t):
        if not x:
            return _sum(0, (r if r < b else b) - (l if l > a else a) + 1, t)
        sm = self.sm
        if l <= a and b <= r:
            return _sum(sm[x], b - a + 1, t)
        L, R = self.L, self.R
        d = _compose(self.tg[x], t)
        m = (a + b) // 2
        if r <= m:
            return self._qSum(L[x], a, m, l, r, d)
        if l > m:
            return self._qSum(R[x], m + 1, b, l, r, d)
        return self._qSum(L[x], a, m, l, r, d) + self._qSum(R[x], m + 1, b, l, r, d)

    # O(logU) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._qSum(1, self.lo, self.hi, l, r, None)

    # max of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with the ancestors' tag t on top
    def _qMax(self, x, a, b, l, r, t):
        if not x:
            return _val(0, t)
        mx = self.mx
        if l <= a and b <= r:
            return _val(mx[x], t)
        L, R = self.L, self.R
        d = _compose(self.tg[x], t)
        m = (a + b) // 2
        if r <= m:
            return self._qMax(L[x], a, m, l, r, d)
        if l > m:
            return self._qMax(R[x], m + 1, b, l, r, d)
        return max(self._qMax(L[x], a, m, l, r, d), self._qMax(R[x], m + 1, b, l, r, d))

    # O(logU) -- max of a[l..r]
    def rangeMax(self, l, r):
        return self._qMax(1, self.lo, self.hi, l, r, None)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._qSum(1, self.lo, self.hi, i, i, None)

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
        self.sm[x] = val
        self.mx[x] = val
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
