# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxPrefixSum-maxSubarraySum-maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeSum/sparse.py
# @operations: maxPrefixSum maxSubarraySum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeSum
# @data-structure-type: lazy-seg-tree
# @complexities:
#   maxPrefixSum: log(U)
#   maxSubarraySum: log(U)
#   maxSuffixSum: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeAssign: log(U)
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[4*log(U)] pre[4*log(U)] suf[4*log(U)] best[4*log(U)]
#   tags: asg[4*log(U)] hasAsg[4*log(U)]
#   other: children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. Lists of nodes

# Range assign with range sum and max prefix / suffix / subarray sum (non-empty pieces), plus point ops.
# A node assigned v over k slots is fully known: sum v * k, and its best prefix / suffix / subarray are
# v * k if v > 0, else v. A block of zeros summarizes to all zeros. Merging is not commutative.
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Updates push a node's tag
# into its children (creating them) before recursing past it; queries never push: they carry the ancestors' tags
# down and apply them to what they return, so they create no nodes. Sparse: lists of nodes; node 0 is the shared
# all-zeros block, node 1 the root; a tag of None means no tag.

ZERO = (0, 0, 0, 0)  # the aggregate of any block of zeros


class SparseMaxSubarrayAssignTree:
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
        s = t * k
        b = s if t > 0 else t
        return s, b, b, b

    # tag o, then tag t
    @staticmethod
    def _compose(o, t):
        return t

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
        return a[0] + b[0], max(a[1], a[0] + b[1]), max(b[2], b[0] + a[2]), max(a[3], b[3], a[2] + b[1])

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

    # O(logU) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, v)

    # O(logU) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        res = self._query(1, self.lo, self.hi, l, r, None)
        return res[0]

    # O(logU) -- best sum of a non-empty prefix of a[l..r]
    def maxPrefixSum(self, l, r):
        res = self._query(1, self.lo, self.hi, l, r, None)
        return res[1]

    # O(logU) -- best sum of a non-empty suffix of a[l..r]
    def maxSuffixSum(self, l, r):
        res = self._query(1, self.lo, self.hi, l, r, None)
        return res[2]

    # O(logU) -- best sum of a non-empty subarray of a[l..r]
    def maxSubarraySum(self, l, r):
        res = self._query(1, self.lo, self.hi, l, r, None)
        return res[3]

    # O(logU) -- a[i]
    def pointGet(self, i):
        res = self._query(1, self.lo, self.hi, i, i, None)
        return res[0]

    # O(logU) -- a[i] = val
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
        self.v[x] = (val, val, val, val)
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
