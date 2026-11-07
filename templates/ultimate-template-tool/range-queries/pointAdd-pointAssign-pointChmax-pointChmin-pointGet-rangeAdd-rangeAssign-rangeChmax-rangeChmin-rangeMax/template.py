# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmax-rangeChmin-rangeMax/template.py
# @operations: getAll maxAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeMax
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeAssign: log(N)
#   rangeChmax: log(N)
#   rangeChmin: log(N)
#   rangeMax: log(N)
#   maxAll: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: mx[2*N]
#   tags: hi[1*N] lo[1*N] add[1*N]
#   other: none
#   note: tags live on the N internal nodes only; each holds one clamp tag x -> min(hi, max(lo, x + add))

INF = float("inf")
NEG = float("-inf")

# Range add / assign / chmin / chmax with range max queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
# Iterative 2N lazy tree: values on the leaves, a tag on each internal node meaning "applied here, not yet pushed
# to my children". The tag is the map x -> min(hi, max(lo, x + add)); these maps compose into the same form, and each is
# monotone, so it sends a node's min / max straight to the new min / max.
# Assign v is the clamp with hi = lo = v.
# An update pushes the tags on its two boundary paths, tags the covering nodes, then rebuilds the two paths.


class ClampMaxTree:
    __slots__ = ("n", "h", "mx", "hi", "lo", "add")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.mx = [NEG] * n + list(arr)
        for x in range(n - 1, 0, -1):
            a, b = self.mx[2 * x], self.mx[2 * x + 1]
            self.mx[x] = a if a > b else b
        self.hi = [INF] * n
        self.lo = [NEG] * n
        self.add = [0] * n

    # apply the map to node x: to its values now, and (if internal) on top of its pending tag
    def _apply(self, x, hi, lo, c):
        v = self.mx[x]
        v += c
        if v < lo:
            v = lo
        if v > hi:
            v = hi
        self.mx[x] = v
        if x < self.n:
            nhi = self.hi[x] + c
            if nhi < lo:
                nhi = lo
            self.hi[x] = nhi if nhi < hi else hi
            nlo = self.lo[x] + c
            if nlo < lo:
                nlo = lo
            if nlo > self.hi[x]:
                nlo = self.hi[x]
            self.lo[x] = nlo
            self.add[x] += c

    # push every tag on the root-to-leaf path of leaf p down one level
    def _push(self, p):
        for s in range(self.h, 0, -1):
            x = p >> s
            if self.hi[x] != INF or self.lo[x] != NEG or self.add[x] != 0:
                hi, lo, c = self.hi[x], self.lo[x], self.add[x]
                self._apply(2 * x, hi, lo, c)
                self._apply(2 * x + 1, hi, lo, c)
                self.hi[x] = INF
                self.lo[x] = NEG
                self.add[x] = 0

    # recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    def _rebuild(self, p):
        while p > 1:
            p >>= 1
            a, b = self.mx[2 * p], self.mx[2 * p + 1]
            v = a if a > b else b
            v += self.add[p]
            if v < self.lo[p]:
                v = self.lo[p]
            if v > self.hi[p]:
                v = self.hi[p]
            self.mx[p] = v

    def _update(self, l, r, hi, lo, c):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        i, j = l0, r0 + 1
        while i < j:
            if i & 1:
                self._apply(i, hi, lo, c)
                i += 1
            if j & 1:
                j -= 1
                self._apply(j, hi, lo, c)
            i >>= 1
            j >>= 1
        self._rebuild(l0)
        self._rebuild(r0)

    # O(logN) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, INF, NEG, v)

    # O(logN) -- a[i] = min(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmin(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, v, NEG, 0)

    # O(logN) -- a[i] = max(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmax(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, INF, v, 0)

    # O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, v, v, 0)

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        arr = self.mx
        res = NEG
        r += 1
        while l < r:
            if l & 1:
                if arr[l] > res:
                    res = arr[l]
                l += 1
            if r & 1:
                r -= 1
                if arr[r] > res:
                    res = arr[r]
            l >>= 1
            r >>= 1
        return res

    # O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    # each node's tag is complete when it is pushed), then read the leaves
    def getAll(self):
        for x in range(1, self.n):
            if self.hi[x] != INF or self.lo[x] != NEG or self.add[x] != 0:
                hi, lo, c = self.hi[x], self.lo[x], self.add[x]
                self._apply(2 * x, hi, lo, c)
                self._apply(2 * x + 1, hi, lo, c)
                self.hi[x] = INF
                self.lo[x] = NEG
                self.add[x] = 0
        return self.mx[self.n:]

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        return self.mx[p]

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        self.mx[p] = val
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

    # O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.n < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.n - 1)
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)
