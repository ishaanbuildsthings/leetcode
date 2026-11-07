# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeChmax/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeChmax
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeChmax: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: val[1*N]
#   tags: B[1*N] C[1*N]
#   other: none
#   note: each internal node holds one pending clamp x -> max(B, x + C); val holds the leaf values

# Range add / chmax + point ops, no range aggregates. All indices 0-based, ranges inclusive.
# Every update is a clamp x -> max(B, x + C); clamps compose into a clamp, but not commutatively, so before tagging
# the covering nodes we push the tags on the paths to l and r (the standard 2N trick for point reads).
NEG = float("-inf")


class AddChmaxTree:
    __slots__ = ("n", "B", "C", "val")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.B = [NEG] * n
        self.C = [0] * n
        self.val = list(arr)

    # apply clamp (b, c) on top of whatever node x already holds
    def _apply(self, x, b, c):
        n = self.n
        if x >= n:
            val = self.val
            v = val[x - n] + c
            if v < b:
                v = b
            val[x - n] = v
        else:
            B, C = self.B, self.C
            q = B[x] + c
            B[x] = b if b > q else q
            C[x] += c

    # O(logN) -- push every pending clamp on leaf p's root-to-leaf path down to its children
    def _push(self, p):
        B, C = self.B, self.C
        apply = self._apply
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            if B[x] != NEG or C[x] != 0:
                b, c = B[x], C[x]
                y = x << 1
                apply(y, b, c)
                apply(y | 1, b, c)
                B[x] = NEG
                C[x] = 0

    def _update(self, l, r, b, c):
        n = self.n
        l += n
        r += n
        self._push(l)
        self._push(r)
        r += 1
        apply = self._apply
        while l < r:
            if l & 1:
                apply(l, b, c)
                l += 1
            if r & 1:
                r -= 1
                apply(r, b, c)
            l >>= 1
            r >>= 1

    # O(logN) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, NEG, v)

    # O(logN) -- a[i] = max(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmax(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, v, 0)

    # O(logN) -- a[i]: start from the leaf and apply ancestors' clamps bottom-up (deeper tags are older); needs
    # 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        B, C = self.B, self.C
        v = self.val[i]
        p = (i + self.n) >> 1
        while p:
            v += C[p]
            b = B[p]
            if v < b:
                v = b
            p >>= 1
        return v

    # O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    # each node's tag is complete when it is pushed), then read the leaves
    def getAll(self):
        B, C = self.B, self.C
        apply = self._apply
        for x in range(1, self.n):
            if B[x] != NEG or C[x] != 0:
                b, c = B[x], C[x]
                apply(2 * x, b, c)
                apply(2 * x + 1, b, c)
                B[x] = NEG
                C[x] = 0
        return list(self.val)

    # O(logN) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self._push(i + self.n)
        self.val[i] = v

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self._push(i + self.n)
        self.val[i] += delta

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
