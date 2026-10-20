# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmin-rangeMax-rangeSum/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmin rangeMax rangeSum
# @data-structure-type: beats
# @complexities:
#   pointAdd: log(N) amortized
#   pointAssign: log(N) amortized
#   pointChmax: log(N) amortized
#   pointChmin: log(N) amortized
#   pointGet: log(N)
#   rangeAssign: log(N) amortized
#   rangeChmin: log(N) amortized
#   rangeMax: log(N)
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: 4n-recursive
#   node: mx[4*N] mx2[4*N] cnt[4*N] tot[4*N]
#   tags: none
#   other: none
#   note: no tag arrays: a node's mx is its pending chmin, and a node with one distinct value (mx2 = sentinel) is a pending assign

SENT = float("-inf")

# Segment tree beats, one side, no add: range chmin / assign, range sum / max, point ops. 0-based, inclusive.
# Each node keeps its max (mx), strict second max (mx2), how many times the max appears, and the sum. A chmin
# with x strictly between mx2 and mx only moves the max copies, so it is O(1) at that node; otherwise it
# descends, and each descent glues two distinct values together, which pays for it: O(log N) amortized, with no
# add tags at all (that is the saving over the beats trees that support range add).
# No tag arrays either: a node's own mx is its pending chmin for the children, and a node holding a single distinct
# value (mx2 == SENT) is its own pending assign.


class ChminSumBeats:
    __slots__ = ("n", "mx", "mx2", "cnt", "tot")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        size = 4 * max(1, n)
        self.mx = [0] * size
        self.mx2 = [SENT] * size
        self.cnt = [0] * size
        self.tot = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        if tl == tr:
            self.mx[i] = self.tot[i] = arr[tl]
            self.mx2[i] = SENT
            self.cnt[i] = 1
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        e, e2, cnt = self.mx, self.mx2, self.cnt
        a, b = 2 * i, 2 * i + 1
        self.tot[i] = self.tot[a] + self.tot[b]
        if e[a] > e[b]:
            e[i], cnt[i] = e[a], cnt[a]
            e2[i] = e2[a] if e2[a] > e[b] else e[b]
        elif e[b] > e[a]:
            e[i], cnt[i] = e[b], cnt[b]
            e2[i] = e2[b] if e2[b] > e[a] else e[a]
        else:
            e[i], cnt[i] = e[a], cnt[a] + cnt[b]
            e2[i] = e2[a] if e2[a] > e2[b] else e2[b]

    # every max copy in node i becomes x (only valid while x is strictly between mx2 and mx)
    def _moveExtreme(self, i, x):
        self.tot[i] += (x - self.mx[i]) * self.cnt[i]
        self.mx[i] = x

    def _setAll(self, i, length, v):
        self.mx[i] = v
        self.mx2[i] = SENT
        self.cnt[i] = length
        self.tot[i] = v * length

    def _push(self, i, tl, tr):
        if tl == tr:
            return
        tm = (tl + tr) // 2
        if self.mx2[i] == SENT:  # one distinct value: a pending assign
            self._setAll(2 * i, tm - tl + 1, self.mx[i])
            self._setAll(2 * i + 1, tr - tm, self.mx[i])
            return
        for c in (2 * i, 2 * i + 1):
            if self.mx[c] > self.mx[i]:  # the child still has values past the parent's cap
                self._moveExtreme(c, self.mx[i])

    def _ch(self, i, tl, tr, l, r, x):
        if r < tl or tr < l or not (self.mx[i] > x):
            return
        if l <= tl and tr <= r and x > self.mx2[i]:
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
            return self.mx[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._ext(2 * i, tl, tm, l, r)
        b = self._ext(2 * i + 1, tm + 1, tr, l, r)
        return a if a > b else b

    # amortized O(logN) -- a[i] = min(a[i], x) for i in [l, r]
    def rangeChmin(self, l, r, x):
        if l <= r and self.n:
            self._ch(1, 0, self.n - 1, l, r, x)

    # amortized O(logN) -- a[i] = x for i in [l, r]
    def rangeAssign(self, l, r, x):
        if l <= r and self.n:
            self._assign(1, 0, self.n - 1, l, r, x)

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._sum(1, 0, self.n - 1, l, r) if l <= r and self.n else 0

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        return self._ext(1, 0, self.n - 1, l, r)

    # O(logN) -- a[i]
    def pointGet(self, i):
        return self._ext(1, 0, self.n - 1, i, i)

    # amortized O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAssign(i, i, val)

    # amortized O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        self.rangeChmin(i, i, val)

    # amortized O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # amortized O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)
