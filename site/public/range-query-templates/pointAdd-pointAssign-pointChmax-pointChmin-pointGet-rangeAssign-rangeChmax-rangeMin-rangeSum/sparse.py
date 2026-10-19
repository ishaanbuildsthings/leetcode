# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeMin rangeSum
# @data-structure-type: beats
# @complexities:
#   pointAdd: log(U) amortized
#   pointAssign: log(U) amortized
#   pointChmax: log(U) amortized
#   pointChmin: log(U) amortized
#   pointGet: log(U)
#   rangeAssign: log(U) amortized
#   rangeChmax: log(U) amortized
#   rangeMin: log(U)
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mn[4*log(U)] mn2[4*log(U)] cnt[4*log(U)] tot[4*log(U)]
#   tags: none
#   other: none
#   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. C++: one shared node pool, call resetPool() between test cases; Python: per-node lists that grow

# Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
# is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
# right before anything descends past a node or pushes its tags. Otherwise the beats logic below is the
# dense tree's, with children in L / R instead of at 2i / 2i + 1.

SENT = float("inf")

# Segment tree beats, one side, no add: range chmax / assign, range sum / min, point ops. 0-based, inclusive.
# Each node keeps its min (mn), strict second min (mn2), how many times the min appears, and the sum. A chmax
# with x strictly between mn2 and mn only moves the min copies, so it is O(1) at that node; otherwise it
# descends, and each descent glues two distinct values together, which pays for it: O(log N) amortized, with no
# add tags at all (that is the saving over the beats trees that support range add).
# No tag arrays either: a node's own mn is its pending chmax for the children, and a node holding a single distinct
# value (mn2 == SENT) is its own pending assign.


class SparseChmaxSumBeats:
    __slots__ = ("lo", "hi", "L", "R", "ln", "mn", "mn2", "cnt", "tot")

    # O(N)
    # O(1) -- all zeros over [lo, hi]; any range of integers works
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        # node 0 is unused; node 1 is the root, one block of hi - lo + 1 zeros
        self.L, self.R, self.ln = [0, 0], [0, 0], [0, 0]
        self.mn = [0] * 2
        self.mn2 = [SENT] * 2
        self.cnt = [0] * 2
        self.tot = [0] * 2
        self._zero(1, hi - lo + 1)

    # node i becomes a block of k zeros (its defaults, plus every count = k)
    def _zero(self, i, k):
        self.ln[i] = k
        self.cnt[i] = k

    # a fresh node: a block of k zeros
    def _node(self, k):
        j = len(self.L)
        self.L.append(0)
        self.R.append(0)
        self.ln.append(0)
        self.mn.append(0)
        self.mn2.append(SENT)
        self.cnt.append(0)
        self.tot.append(0)
        self._zero(j, k)
        return j

    # create node i's children (blocks of zeros: the left one gets the extra slot) if it has none yet
    def _kids(self, i):
        if not self.L[i] and self.ln[i] > 1:
            k = self.ln[i]
            self.L[i] = self._node((k + 1) // 2)
            self.R[i] = self._node(k // 2)

    def _pull(self, i):
        e, e2, cnt = self.mn, self.mn2, self.cnt
        a, b = self.L[i], self.R[i]
        self.tot[i] = self.tot[a] + self.tot[b]
        if e[a] < e[b]:
            e[i], cnt[i] = e[a], cnt[a]
            e2[i] = e2[a] if e2[a] < e[b] else e[b]
        elif e[b] < e[a]:
            e[i], cnt[i] = e[b], cnt[b]
            e2[i] = e2[b] if e2[b] < e[a] else e[a]
        else:
            e[i], cnt[i] = e[a], cnt[a] + cnt[b]
            e2[i] = e2[a] if e2[a] < e2[b] else e2[b]

    # every min copy in node i becomes x (only valid while x is strictly between mn2 and mn)
    def _moveExtreme(self, i, x):
        self.tot[i] += (x - self.mn[i]) * self.cnt[i]
        self.mn[i] = x

    def _setAll(self, i, length, v):
        self.mn[i] = v
        self.mn2[i] = SENT
        self.cnt[i] = length
        self.tot[i] = v * length

    def _push(self, i, tl, tr):
        self._kids(i)
        if tl == tr:
            return
        self._kids(i)
        tm = (tl + tr) // 2
        if self.mn2[i] == SENT:  # one distinct value: a pending assign
            self._setAll(self.L[i], tm - tl + 1, self.mn[i])
            self._setAll(self.R[i], tr - tm, self.mn[i])
            return
        for c in (self.L[i], self.R[i]):
            if self.mn[c] < self.mn[i]:  # the child still has values past the parent's cap
                self._moveExtreme(c, self.mn[i])

    def _ch(self, i, tl, tr, l, r, x):
        if r < tl or tr < l or not (self.mn[i] < x):
            return
        if l <= tl and tr <= r and x < self.mn2[i]:
            self._moveExtreme(i, x)
            return
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        self._ch(self.L[i], tl, tm, l, r, x)
        self._ch(self.R[i], tm + 1, tr, l, r, x)
        self._pull(i)

    def _assign(self, i, tl, tr, l, r, v):
        if r < tl or tr < l:
            return
        if l <= tl and tr <= r:
            self._setAll(i, tr - tl + 1, v)
            return
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        self._assign(self.L[i], tl, tm, l, r, v)
        self._assign(self.R[i], tm + 1, tr, l, r, v)
        self._pull(i)

    def _sum(self, i, tl, tr, l, r):
        if r < tl or tr < l:
            return 0
        if l <= tl and tr <= r:
            return self.tot[i]
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        return self._sum(self.L[i], tl, tm, l, r) + self._sum(self.R[i], tm + 1, tr, l, r)

    def _ext(self, i, tl, tr, l, r):
        if r < tl or tr < l:
            return SENT
        if l <= tl and tr <= r:
            return self.mn[i]
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        a = self._ext(self.L[i], tl, tm, l, r)
        b = self._ext(self.R[i], tm + 1, tr, l, r)
        return a if a < b else b

    # amortized O(logN) -- a[i] = max(a[i], x) for i in [l, r]
    def rangeChmax(self, l, r, x):
        if l <= r:
            self._ch(1, self.lo, self.hi, l, r, x)

    # amortized O(logN) -- a[i] = x for i in [l, r]
    def rangeAssign(self, l, r, x):
        if l <= r:
            self._assign(1, self.lo, self.hi, l, r, x)

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._sum(1, self.lo, self.hi, l, r) if l <= r else 0

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        return self._ext(1, self.lo, self.hi, l, r)

    # O(logN) -- a[i]
    def pointGet(self, i):
        return self._ext(1, self.lo, self.hi, i, i)

    # amortized O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAssign(i, i, val)

    # amortized O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        self.rangeChmax(i, i, val)

    # amortized O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)

    # amortized O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)
