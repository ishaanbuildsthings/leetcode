# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeMax rangeMin rangeSum
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
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] mn[2*N] mx[2*N]
#   tags: add[1*N]
#   other: none
#   note: tags live on the N internal nodes only; each holds a pending add

INF = float("inf")
NEG = float("-inf")

# Range add with range sum / min / max queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
# Iterative 2N lazy tree: values on the leaves, and on each internal node a pending add, meaning "applied here, not
# yet pushed to my children". An update pushes the tags on its two boundary paths, tags the covering nodes, then
# rebuilds the two paths. A covering node at level s is a perfect subtree of 2^s leaves, so its length is 1 << s.


class AddSumMinMaxTree:
    __slots__ = ("n", "h", "sm", "mn", "mx", "add")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.mn = [INF] * n + list(arr)
        self.mx = [NEG] * n + list(arr)
        for x in range(n - 1, 0, -1):
            self.sm[x] = self.sm[2 * x] + self.sm[2 * x + 1]
            self.mn[x] = min(self.mn[2 * x], self.mn[2 * x + 1])
            self.mx[x] = max(self.mx[2 * x], self.mx[2 * x + 1])
        self.add = [0] * n

    # add c to every slot of node x, which covers k slots
    def _applyAdd(self, x, k, c):
        self.sm[x] += c * k
        self.mn[x] += c
        self.mx[x] += c
        if x < self.n:
            self.add[x] += c

    # push every tag on the root-to-leaf path of leaf p down one level
    def _push(self, p):
        for s in range(self.h, 0, -1):
            x = p >> s
            k = 1 << (s - 1)
            if self.add[x]:
                self._applyAdd(2 * x, k, self.add[x])
                self._applyAdd(2 * x + 1, k, self.add[x])
                self.add[x] = 0

    # recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    def _rebuild(self, p):
        k = 1
        while p > 1:
            p >>= 1
            k <<= 1
            self.sm[p] = self.sm[2 * p] + self.sm[2 * p + 1] + self.add[p] * k
            self.mn[p] = min(self.mn[2 * p], self.mn[2 * p + 1]) + self.add[p]
            self.mx[p] = max(self.mx[2 * p], self.mx[2 * p + 1]) + self.add[p]

    # O(logN) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        lo, hi, k = l0, r0 + 1, 1
        while lo < hi:
            if lo & 1:
                self._applyAdd(lo, k, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._applyAdd(hi, k, v)
            lo >>= 1
            hi >>= 1
            k <<= 1
        self._rebuild(l0)
        self._rebuild(r0)

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        if l > r:
            return 0
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        arr = self.sm
        res = 0
        r += 1
        while l < r:
            if l & 1:
                res += arr[l]
                l += 1
            if r & 1:
                r -= 1
                res += arr[r]
            l >>= 1
            r >>= 1
        return res

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        if l > r:
            return INF
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
        if l > r:
            return NEG
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
        return self.sm[p]

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        p = i + self.n
        self._push(p)
        self.sm[p] = self.mn[p] = self.mx[p] = val
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
