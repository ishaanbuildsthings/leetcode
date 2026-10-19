# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeMax rangeMin
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeMax: log(N)
#   rangeMin: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: mn[2*N] mx[2*N]
#   tags: add[1*N]
#   other: none
#   note: tags live on the N internal nodes only; each holds one clamp tag x -> x + add

INF = float("inf")
NEG = float("-inf")

# Range add with range min / max queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
# Iterative 2N lazy tree: values on the leaves, a tag on each internal node meaning "applied here, not yet pushed
# to my children". The tag is the map x -> x + add; these maps compose into the same form, and each is
# monotone, so it sends a node's min / max straight to the new min / max.
# An update pushes the tags on its two boundary paths, tags the covering nodes, then rebuilds the two paths.


class AddMinMaxTree:
    __slots__ = ("n", "h", "mn", "mx", "add")

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
        self.add = [0] * n

    # apply the map to node x: to its values now, and (if internal) on top of its pending tag
    def _apply(self, x, c):
        v = self.mn[x]
        v += c
        self.mn[x] = v
        v = self.mx[x]
        v += c
        self.mx[x] = v
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
            a, b = self.mx[2 * p], self.mx[2 * p + 1]
            v = a if a > b else b
            v += self.add[p]
            self.mx[p] = v

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

    # O(logN) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        self._update(l, r, v)

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
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

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
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

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        self._push(p)
        return self.mn[p]

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        p = i + self.n
        self._push(p)
        self.mn[p] = self.mx[p] = val
        self._rebuild(p)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
