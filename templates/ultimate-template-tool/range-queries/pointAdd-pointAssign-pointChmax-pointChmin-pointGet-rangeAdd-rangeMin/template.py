# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeMin/template.py
# @operations: getAll minAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeMin
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeMin: log(N)
#   minAll: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: mn[2*N]
#   tags: add[1*N]
#   other: none
#   note: tags live on the N internal nodes only; each holds one clamp tag x -> x + add

INF = float("inf")
NEG = float("-inf")

# Range add with range min queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
# Iterative 2N lazy tree: values on the leaves, a tag on each internal node meaning "applied here, not yet pushed
# to my children". The tag is the map x -> x + add; these maps compose into the same form, and each is
# monotone, so it sends a node's min / max straight to the new min / max.
# An update pushes the tags on its two boundary paths, tags the covering nodes, then rebuilds the two paths.


class AddMinTree:
    __slots__ = ("n", "h", "mn", "add")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.mn = [INF] * n + list(arr)
        for x in range(n - 1, 0, -1):
            a, b = self.mn[2 * x], self.mn[2 * x + 1]
            self.mn[x] = a if a < b else b
        self.add = [0] * n

    # apply the map to node x: to its values now, and (if internal) on top of its pending tag
    def _apply(self, x, c):
        v = self.mn[x]
        v += c
        self.mn[x] = v
        if x < self.n:
            self.add[x] += c

    # push every tag on the root-to-leaf path of leaf p down one level
    def _push(self, p):
        for s in range(self.h, 0, -1):
            x = p >> s
            if self.add[x] != 0:
                c = self.add[x]
                self._apply(2 * x, c)
                self._apply(2 * x + 1, c)
                self.add[x] = 0

    # recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    def _rebuild(self, p):
        while p > 1:
            p >>= 1
            a, b = self.mn[2 * p], self.mn[2 * p + 1]
            v = a if a < b else b
            v += self.add[p]
            self.mn[p] = v

    def _update(self, l, r, c):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        i, j = l0, r0 + 1
        while i < j:
            if i & 1:
                self._apply(i, c)
                i += 1
            if j & 1:
                j -= 1
                self._apply(j, c)
            i >>= 1
            j >>= 1
        self._rebuild(l0)
        self._rebuild(r0)

    # O(logN) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, v)

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        arr = self.mn
        res = INF
        r += 1
        while l < r:
            if l & 1:
                if arr[l] < res:
                    res = arr[l]
                l += 1
            if r & 1:
                r -= 1
                if arr[r] < res:
                    res = arr[r]
            l >>= 1
            r >>= 1
        return res

    # O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    # each node's tag is complete when it is pushed), then read the leaves
    def getAll(self):
        for x in range(1, self.n):
            if self.add[x] != 0:
                c = self.add[x]
                self._apply(2 * x, c)
                self._apply(2 * x + 1, c)
                self.add[x] = 0
        return self.mn[self.n:]

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        return self.mn[p]

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        self.mn[p] = val
        self._rebuild(p)

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logN) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val); needs needs 0 <= i < n, else IndexError, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")

    # O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.n < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.n - 1)
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)
