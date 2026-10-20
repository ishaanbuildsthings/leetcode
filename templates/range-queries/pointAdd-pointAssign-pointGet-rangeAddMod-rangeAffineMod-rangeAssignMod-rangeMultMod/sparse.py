# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod-rangeAffineMod-rangeAssignMod-rangeMultMod/sparse.py
# @operations: pointAdd pointAssign pointGet rangeAddMod rangeAffineMod rangeAssignMod rangeMultMod
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointGet: log(U)
#   rangeAddMod: log(U)
#   rangeAffineMod: log(U)
#   rangeAssignMod: log(U)
#   rangeMultMod: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[4*log(U)]
#   tags: mul[4*log(U)] add[4*log(U)]
#   other: children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. a leaf's value is sm (internal nodes keep no aggregate). Lists of nodes

# Range affine maps mod p (add, mult and assign are special cases: x -> 1x + v, mx + 0, 0x + v),
# plus point ops. Values are residues in [0, mod). A tag is the map x -> mul * x + add; maps compose into
# the same form. Only leaves' values matter, so nothing is pulled.
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Updates push a node's tag
# into its children (creating them) before recursing past it; queries never push: they carry the ancestors' tags
# down and apply them to what they return, so they create no nodes. Sparse: lists of nodes; node 0 is the shared
# all-zeros block, node 1 the root; a tag of None means no tag.

ZERO = 0  # the aggregate of any block of zeros


class SparseAffineTree:
    __slots__ = ("lo", "hi", "L", "R", "v", "tg", "mod")

    # O(1)
    def __init__(self, lo, hi, mod=1000000007):
        self.lo, self.hi = lo, hi
        self.L, self.R = [0, 0], [0, 0]
        self.v = [ZERO, ZERO]
        self.tg = [None, None]
        self.mod = mod

    def _kid(self, x, right):  # child of x, created as a block of zeros if missing
        kids = self.R if right else self.L
        y = kids[x]
        if not y:
            y = len(self.L)
            self.L.append(0)
            self.R.append(0)
            self.v.append(ZERO)
            self.tg.append(None)
            kids[x] = y
        return y

    # the aggregate v of k slots after tag t
    def _tagged(self, v, k, t):
        return (t[0] * v + t[1]) % self.mod

    # tag o, then tag t
    def _compose(self, o, t):
        return t[0] * o[0] % self.mod, (t[0] * o[1] + t[1]) % self.mod

    # node x (k slots) takes tag t: its aggregate now, its children later
    def _apply(self, x, k, t):
        self.v[x] = self._tagged(self.v[x], k, t)
        o = self.tg[x]
        self.tg[x] = t if o is None else self._compose(o, t)

    # move x's tag (x covers [a, b]) into its children, creating them
    def _push(self, x, a, b):
        t = self.tg[x]
        if t is not None:
            m = (a + b) // 2
            self._apply(self._kid(x, 0), m - a + 1, t)
            self._apply(self._kid(x, 1), b - m, t)
            self.tg[x] = None

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

    # aggregate of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with the ancestors' tag t on top
    def _query(self, x, a, b, l, r, t):
        if not x:
            return ZERO if t is None else self._tagged(ZERO, (r if r < b else b) - (l if l > a else a) + 1, t)
        if l <= a and b <= r:
            return self.v[x] if t is None else self._tagged(self.v[x], b - a + 1, t)
        o = self.tg[x]
        d = o if t is None else (t if o is None else self._compose(o, t))
        m = (a + b) // 2
        if r <= m:
            return self._query(self.L[x], a, m, l, r, d)
        return self._query(self.R[x], m + 1, b, l, r, d)

    # O(logU) -- a[i] = a[i] + v (mod p) for i in [l, r]
    def rangeAddMod(self, l, r, v):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, (1, v % self.mod))

    # O(logU) -- a[i] = a[i] * m (mod p) for i in [l, r]
    def rangeMultMod(self, l, r, m):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, (m % self.mod, 0))

    # O(logU) -- a[i] = v (mod p) for i in [l, r]
    def rangeAssignMod(self, l, r, v):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, (0, v % self.mod))

    # O(logU) -- a[i] = a[i] * mult + add (mod p) for i in [l, r]
    def rangeAffineMod(self, l, r, mult, add):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, (mult % self.mod, add % self.mod))

    # O(logU) -- a[i], in [0, mod)
    def pointGet(self, i):
        res = self._query(1, self.lo, self.hi, i, i, None)
        return res

    # O(logU) -- a[i] = val (mod p)
    def pointAssign(self, i, val):
        path = []
        x, a, b = 1, self.lo, self.hi
        while a < b:
            self._push(x, a, b)
            path.append(x)
            m = (a + b) // 2
            if i <= m:
                x, b = self._kid(x, 0), m
            else:
                x, a = self._kid(x, 1), m + 1
        self.v[x] = val % self.mod

    # O(logU) -- a[i] += delta (mod p)
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)
