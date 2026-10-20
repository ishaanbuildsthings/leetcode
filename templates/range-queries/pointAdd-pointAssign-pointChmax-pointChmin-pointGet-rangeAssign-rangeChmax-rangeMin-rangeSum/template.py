# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmax-rangeMin-rangeSum/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeMin rangeSum
# @data-structure-type: beats
# @complexities:
#   pointAdd: log(N) amortized
#   pointAssign: log(N) amortized
#   pointChmax: log(N) amortized
#   pointChmin: log(N) amortized
#   pointGet: log(N)
#   rangeAssign: log(N) amortized
#   rangeChmax: log(N) amortized
#   rangeMin: log(N)
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: 4n-recursive
#   node: mn[4*N] mn2[4*N] cnt[4*N] tot[4*N]
#   tags: none
#   other: none
#   note: no tag arrays: a node's mn is its pending chmax, and a node with one distinct value (mn2 = sentinel) is a pending assign

SENT = float("inf")

# Segment tree beats, one side, no add: range chmax / assign, range sum / min, point ops. 0-based, inclusive.
# Each node keeps its min (mn), strict second min (mn2), how many times the min appears, and the sum. A chmax
# with x strictly between mn2 and mn only moves the min copies, so it is O(1) at that node; otherwise it
# descends, and each descent glues two distinct values together, which pays for it: O(log N) amortized, with no
# add tags at all (that is the saving over the beats trees that support range add).
# No tag arrays either: a node's own mn is its pending chmax for the children, and a node holding a single distinct
# value (mn2 == SENT) is its own pending assign.


class ChmaxSumBeats:
    __slots__ = ("n", "mn", "mn2", "cnt", "tot")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        size = 4 * max(1, n)
        self.mn = [0] * size
        self.mn2 = [SENT] * size
        self.cnt = [0] * size
        self.tot = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        if tl == tr:
            self.mn[i] = self.tot[i] = arr[tl]
            self.mn2[i] = SENT
            self.cnt[i] = 1
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        e, e2, cnt = self.mn, self.mn2, self.cnt
        a, b = 2 * i, 2 * i + 1
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
        if tl == tr:
            return
        tm = (tl + tr) // 2
        if self.mn2[i] == SENT:  # one distinct value: a pending assign
            self._setAll(2 * i, tm - tl + 1, self.mn[i])
            self._setAll(2 * i + 1, tr - tm, self.mn[i])
            return
        for c in (2 * i, 2 * i + 1):
            if self.mn[c] < self.mn[i]:  # the child still has values past the parent's cap
                self._moveExtreme(c, self.mn[i])

    def _ch(self, i, tl, tr, l, r, x):
        if r < tl or tr < l or not (self.mn[i] < x):
            return
        if l <= tl and tr <= r and x < self.mn2[i]:
            self._moveExtreme(i, x)
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._ch(2 * i, tl, tm, l, r, x)
        self._ch(2 * i + 1, tm + 1, tr, l, r, x)
        self._pull(i)

    def _assign(self, i, tl, tr, l, r, v):
        if r < tl or tr < l:
            return
        if l <= tl and tr <= r:
            self._setAll(i, tr - tl + 1, v)
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._assign(2 * i, tl, tm, l, r, v)
        self._assign(2 * i + 1, tm + 1, tr, l, r, v)
        self._pull(i)

    def _sum(self, i, tl, tr, l, r):
        if r < tl or tr < l:
            return 0
        if l <= tl and tr <= r:
            return self.tot[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        return self._sum(2 * i, tl, tm, l, r) + self._sum(2 * i + 1, tm + 1, tr, l, r)

    def _ext(self, i, tl, tr, l, r):
        if r < tl or tr < l:
            return SENT
        if l <= tl and tr <= r:
            return self.mn[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._ext(2 * i, tl, tm, l, r)
        b = self._ext(2 * i + 1, tm + 1, tr, l, r)
        return a if a < b else b

    # amortized O(logN) -- a[i] = max(a[i], x) for i in [l, r]
    def rangeChmax(self, l, r, x):
        if l <= r and self.n:
            self._ch(1, 0, self.n - 1, l, r, x)

    # amortized O(logN) -- a[i] = x for i in [l, r]
    def rangeAssign(self, l, r, x):
        if l <= r and self.n:
            self._assign(1, 0, self.n - 1, l, r, x)

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._sum(1, 0, self.n - 1, l, r) if l <= r and self.n else 0

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        return self._ext(1, 0, self.n - 1, l, r)

    # O(logN) -- a[i]
    def pointGet(self, i):
        return self._ext(1, 0, self.n - 1, i, i)

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
