# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeOrApply-rangeOrQuery-rangeSum-rangeXorApply/sparse.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeOrApply rangeOrQuery rangeSum rangeXorApply
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(U)*log(U)
#   pointAssign: log(U)*log(U)
#   pointChmax: log(U)*log(U)
#   pointChmin: log(U)*log(U)
#   pointGet: log(U)*log(U)
#   rangeAndApply: log(U)*log(U)
#   rangeAndQuery: log(U)*log(U)
#   rangeOrApply: log(U)*log(U)
#   rangeOrQuery: log(U)*log(U)
#   rangeSum: log(U)*log(U)
#   rangeXorApply: log(U)*log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: cnt[4*log(U)*log(U)]
#   tags: a[4*log(U)] x[4*log(U)]
#   other: children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. every node keeps BITS counts (BITS = 20, the second log); lists of nodes

BITS = 20  # values live in [0, 2^BITS)
FULL = (1 << BITS) - 1

# Range and= / or= / xor= with range sum / and / or queries, plus point ops. Values live in [0, 2^BITS).
# Each node counts, for every bit, how many of its values have that bit set. Every update is a bit map
# v -> (v & a) ^ x, and per bit that is keep, force 0 (count = 0), force 1, or flip (count = length - count),
# so every update is an ordinary lazy tag. Sum = sum over bits of count * 2^bit.
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Updates push a node's tag
# into its children (creating them) before recursing past it; queries never push: they carry the ancestors' tags
# down and apply them to what they return, so they create no nodes. Sparse: lists of nodes; node 0 is the shared
# all-zeros block, node 1 the root; a tag of None means no tag.

ZERO = (0,) * BITS  # the aggregate of any block of zeros


class SparseBitCountTree:
    __slots__ = ("lo", "hi", "L", "R", "v", "tg")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.L, self.R = [0, 0], [0, 0]
        self.v = [ZERO, ZERO]
        self.tg = [None, None]

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
    @staticmethod
    def _tagged(v, k, t):
        a, x = t
        return tuple(((k - c) if x >> b & 1 else c) if a >> b & 1 else (k if x >> b & 1 else 0) for b, c in enumerate(v))

    # tag o, then tag t
    @staticmethod
    def _compose(o, t):
        return o[0] & t[0], (o[1] & t[0]) ^ t[1]

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

    def _pull(self, x):
        v = self.v
        v[x] = self._merge(v[self.L[x]], v[self.R[x]])

    @staticmethod
    def _merge(a, b):
        return tuple(map(int.__add__, a, b))

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
        self._pull(x)

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
        if l > m:
            return self._query(self.R[x], m + 1, b, l, r, d)
        return self._merge(self._query(self.L[x], a, m, l, r, d), self._query(self.R[x], m + 1, b, l, r, d))

    # O(logU) -- a[i] &= X for i in [l, r]
    def rangeAndApply(self, l, r, X):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, (X & FULL, 0))

    # O(logU) -- a[i] |= X for i in [l, r]
    def rangeOrApply(self, l, r, X):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, (~X & FULL, X & FULL))

    # O(logU) -- a[i] ^= X for i in [l, r]
    def rangeXorApply(self, l, r, X):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, (FULL, X & FULL))

    # O(logU) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        res = self._query(1, self.lo, self.hi, l, r, None)
        return sum(c << b for b, c in enumerate(res))

    # O(logU) -- a[l] & ... & a[r]
    def rangeAndQuery(self, l, r):
        res = self._query(1, self.lo, self.hi, l, r, None)
        return sum(1 << b for b, c in enumerate(res) if c == r - l + 1)

    # O(logU) -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r):
        res = self._query(1, self.lo, self.hi, l, r, None)
        return sum(1 << b for b, c in enumerate(res) if c)

    # O(logU) -- a[i]
    def pointGet(self, i):
        res = self._query(1, self.lo, self.hi, i, i, None)
        return sum(c << b for b, c in enumerate(res))

    # O(logU) -- a[i] = val & FULL
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
        self.v[x] = tuple(val >> b & 1 for b in range(BITS))
        for y in reversed(path):
            self._pull(y)

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
