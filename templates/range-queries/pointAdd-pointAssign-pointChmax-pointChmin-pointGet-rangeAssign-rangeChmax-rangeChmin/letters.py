# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmax-rangeChmin/letters.py
# @operations: getAll pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeChmin
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAssign: log(N)
#   rangeChmax: log(N)
#   rangeChmin: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: val[1*N]
#   tags: A[1*N] B[1*N]
#   other: none
#   note: each internal node holds one pending clamp x -> min(A, max(B, x)); val holds the leaf values

# Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
# operations that make sense on characters are listed.
# Range assign / chmax / chmin + point ops, no range aggregates. All indices 0-based, ranges inclusive.
# Every update is a clamp x -> min(A, max(B, x)); clamps compose into a clamp, but not commutatively, so before tagging
# the covering nodes we push the tags on the paths to l and r (the standard 2N trick for point reads).
INF = chr(0x10FFFF)
NEG = ""


class ChminChmaxTree:
    __slots__ = ("n", "A", "B", "val")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.A = [INF] * n
        self.B = [NEG] * n
        self.val = list(arr)

    # apply clamp (a, b) on top of whatever node x already holds
    def _apply(self, x, a, b):
        n = self.n
        if x >= n:
            val = self.val
            v = val[x - n]
            if v < b:
                v = b
            if v > a:
                v = a
            val[x - n] = v
        else:
            A, B = self.A, self.B
            na = A[x] if A[x] > b else b
            if a < na:
                na = a
            nb = B[x] if B[x] > b else b
            A[x] = na
            B[x] = nb if nb < na else na

    # O(logN) -- push every pending clamp on leaf p's root-to-leaf path down to its children
    def _push(self, p):
        A, B = self.A, self.B
        apply = self._apply
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            if A[x] != INF or B[x] != NEG:
                a, b = A[x], B[x]
                y = x << 1
                apply(y, a, b)
                apply(y | 1, a, b)
                A[x] = INF
                B[x] = NEG

    def _update(self, l, r, a, b):
        n = self.n
        l += n
        r += n
        self._push(l)
        self._push(r)
        r += 1
        apply = self._apply
        while l < r:
            if l & 1:
                apply(l, a, b)
                l += 1
            if r & 1:
                r -= 1
                apply(r, a, b)
            l >>= 1
            r >>= 1

    # O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, v, v)

    # O(logN) -- a[i] = max(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmax(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, INF, v)

    # O(logN) -- a[i] = min(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmin(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, v, NEG)

    # O(logN) -- a[i]: start from the leaf and apply ancestors' clamps bottom-up (deeper tags are older); needs
    # 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        A, B = self.A, self.B
        v = self.val[i]
        p = (i + self.n) >> 1
        while p:
            b = B[p]
            if v < b:
                v = b
            a = A[p]
            if v > a:
                v = a
            p >>= 1
        return v

    # O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    # each node's tag is complete when it is pushed), then read the leaves
    def getAll(self):
        A, B = self.A, self.B
        apply = self._apply
        for x in range(1, self.n):
            if A[x] != INF or B[x] != NEG:
                a, b = A[x], B[x]
                apply(2 * x, a, b)
                apply(2 * x + 1, a, b)
                A[x] = INF
                B[x] = NEG
        return list(self.val)

    # O(logN) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self._push(i + self.n)
        self.val[i] = v

    # O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self._push(i + self.n)
        if v > self.val[i]:
            self.val[i] = v

    # O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self._push(i + self.n)
        if v < self.val[i]:
            self.val[i] = v
