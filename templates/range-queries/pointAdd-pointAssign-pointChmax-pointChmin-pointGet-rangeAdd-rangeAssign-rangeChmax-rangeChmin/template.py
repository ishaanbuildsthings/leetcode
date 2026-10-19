# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin
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
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: val[1*N]
#   tags: A[1*N] B[1*N] C[1*N]
#   other: none
#   note: each internal node holds one pending clamp x -> min(A, max(B, x + C)); val holds the leaf values

# Range add / assign / chmax / chmin + point ops, no range aggregates. All indices 0-based, ranges inclusive.
# Every update is a clamp f(x) = min(A, max(B, x + C)) with B <= A:
#   add v -> (INF, -INF, v)    chmax v -> (INF, v, 0)    chmin v -> (v, -INF, 0)    assign v -> (v, v, 0)
# Clamps compose into a clamp, but not commutatively, so before tagging the covering nodes we push the tags on
# the paths to l and r (the standard 2N trick for non-commutative updates with point reads).
INF = float("inf")


class ClampTree:
    __slots__ = ("n", "A", "B", "C", "val")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.A = [INF] * n
        self.B = [-INF] * n
        self.C = [0] * n
        self.val = list(arr)

    # apply clamp (a, b, c) on top of whatever node x already holds
    def _apply(self, x, a, b, c):
        n = self.n
        if x >= n:
            val = self.val
            v = val[x - n] + c
            if v < b:
                v = b
            if v > a:
                v = a
            val[x - n] = v
        else:
            A, B, C = self.A, self.B, self.C
            p = A[x] + c
            q = B[x] + c
            na = p if p > b else b
            if a < na:
                na = a
            nb = q if q > b else b
            A[x] = na
            B[x] = nb if nb < na else na
            C[x] += c

    # O(logN) -- push every pending clamp on leaf p's root-to-leaf path down to its children
    def _push(self, p):
        A, B, C = self.A, self.B, self.C
        apply = self._apply
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            a, b, c = A[x], B[x], C[x]
            if a != INF or b != -INF or c:
                y = x << 1
                apply(y, a, b, c)
                apply(y | 1, a, b, c)
                A[x] = INF
                B[x] = -INF
                C[x] = 0

    def _update(self, l, r, a, b, c):
        n = self.n
        l += n
        r += n
        self._push(l)
        self._push(r)
        r += 1
        apply = self._apply
        while l < r:
            if l & 1:
                apply(l, a, b, c)
                l += 1
            if r & 1:
                r -= 1
                apply(r, a, b, c)
            l >>= 1
            r >>= 1

    # O(logN) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        self._update(l, r, INF, -INF, v)

    # O(logN) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        self._update(l, r, v, v, 0)

    # O(logN) -- a[i] = max(a[i], v) for i in [l, r]
    def rangeChmax(self, l, r, v):
        self._update(l, r, INF, v, 0)

    # O(logN) -- a[i] = min(a[i], v) for i in [l, r]
    def rangeChmin(self, l, r, v):
        self._update(l, r, v, -INF, 0)

    # O(logN) -- a[i]: start from the leaf and apply ancestors' clamps bottom-up (deeper tags are older)
    def pointGet(self, i):
        A, B, C = self.A, self.B, self.C
        v = self.val[i]
        p = (i + self.n) >> 1
        while p:
            v += C[p]
            b = B[p]
            if v < b:
                v = b
            a = A[p]
            if v > a:
                v = a
            p >>= 1
        return v

    # O(logN) -- a[i] = v
    def pointAssign(self, i, v):
        self._push(i + self.n)
        self.val[i] = v

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self._push(i + self.n)
        self.val[i] += delta

    # O(logN) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        self._push(i + self.n)
        if v > self.val[i]:
            self.val[i] = v

    # O(logN) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        self._push(i + self.n)
        if v < self.val[i]:
            self.val[i] = v
