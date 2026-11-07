# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeChmax-rangeMax-rangeMin/letters.py
# @operations: getAll maxAll minAll pointAssign pointChmax pointChmin pointGet rangeChmax rangeMax rangeMin
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeChmax: log(N)
#   rangeMax: log(N)
#   rangeMin: log(N)
#   minAll: log(N)
#   maxAll: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: mn[2*N] mx[2*N]
#   tags: lo[1*N]
#   other: none
#   note: tags live on the N internal nodes only; each holds one clamp tag x -> max(lo, x)

# Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
# operations that make sense on characters are listed.
INF = chr(0x10FFFF)
NEG = ""

# Range chmax with range min / max queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
# Iterative 2N lazy tree: values on the leaves, a tag on each internal node meaning "applied here, not yet pushed
# to my children". The tag is the map x -> max(lo, x); these maps compose into the same form, and each is
# monotone, so it sends a node's min / max straight to the new min / max.
# An update pushes the tags on its two boundary paths, tags the covering nodes, then rebuilds the two paths.


class ChmaxMinMaxTree:
    __slots__ = ("n", "h", "mn", "mx", "lo")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.mn = [INF] * n + list(arr)
        self.mx = [NEG] * n + list(arr)
        for x in range(n - 1, 0, -1):
            a, b = self.mn[2 * x], self.mn[2 * x + 1]
            self.mn[x] = a if a < b else b
            a, b = self.mx[2 * x], self.mx[2 * x + 1]
            self.mx[x] = a if a > b else b
        self.lo = [NEG] * n

    # apply the map to node x: to its values now, and (if internal) on top of its pending tag
    def _apply(self, x, lo):
        v = self.mn[x]
        if v < lo:
            v = lo
        self.mn[x] = v
        v = self.mx[x]
        if v < lo:
            v = lo
        self.mx[x] = v
        if x < self.n:
            nlo = self.lo[x]
            if nlo < lo:
                nlo = lo
            self.lo[x] = nlo

    # push every tag on the root-to-leaf path of leaf p down one level
    def _push(self, p):
        for s in range(self.h, 0, -1):
            x = p >> s
            if self.lo[x] != NEG:
                lo = self.lo[x]
                self._apply(2 * x, lo)
                self._apply(2 * x + 1, lo)
                self.lo[x] = NEG

    # recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    def _rebuild(self, p):
        while p > 1:
            p >>= 1
            a, b = self.mn[2 * p], self.mn[2 * p + 1]
            v = a if a < b else b
            if v < self.lo[p]:
                v = self.lo[p]
            self.mn[p] = v
            a, b = self.mx[2 * p], self.mx[2 * p + 1]
            v = a if a > b else b
            if v < self.lo[p]:
                v = self.lo[p]
            self.mx[p] = v

    def _update(self, l, r, lo):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        i, j = l0, r0 + 1
        while i < j:
            if i & 1:
                self._apply(i, lo)
                i += 1
            if j & 1:
                j -= 1
                self._apply(j, lo)
            i >>= 1
            j >>= 1
        self._rebuild(l0)
        self._rebuild(r0)

    # O(logN) -- a[i] = max(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmax(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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
            if self.lo[x] != NEG:
                lo = self.lo[x]
                self._apply(2 * x, lo)
                self._apply(2 * x + 1, lo)
                self.lo[x] = NEG
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
        self.mn[p] = self.mx[p] = val
        self._rebuild(p)

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

    # O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.n < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.n - 1)
        if self.n < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.n - 1)
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)
