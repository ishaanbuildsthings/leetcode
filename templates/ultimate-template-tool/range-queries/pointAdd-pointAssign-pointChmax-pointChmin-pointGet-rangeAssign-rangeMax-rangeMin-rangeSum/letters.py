# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeMax-rangeMin-rangeSum/letters.py
# @operations: getAll maxAll minAll pointAssign pointChmax pointChmin pointGet rangeAssign rangeMax rangeMin
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAssign: log(N)
#   rangeMax: log(N)
#   rangeMin: log(N)
#   minAll: log(N)
#   maxAll: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] mn[2*N] mx[2*N]
#   tags: asg[1*N] hasAsg[1*N]
#   other: none
#   note: tags live on the N internal nodes only; each holds a pending assign

# Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
# operations that make sense on characters are listed.
INF = chr(0x10FFFF)
NEG = ""

# Range assign with range sum / min / max queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
# Iterative 2N lazy tree: values on the leaves, and on each internal node a pending assign, meaning "applied here, not
# yet pushed to my children". An update pushes the tags on its two boundary paths, tags the covering nodes, then
# rebuilds the two paths. A covering node at level s is a perfect subtree of 2^s leaves, so its length is 1 << s.


class AssignSumMinMaxTree:
    __slots__ = ("n", "h", "sm", "mn", "mx", "asg", "hasAsg")

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
        self.asg = [0] * n
        self.hasAsg = [False] * n

    # set every slot of node x (k slots) to v
    def _applyAssign(self, x, k, v):
        self.sm[x] = v * k
        self.mn[x] = self.mx[x] = v
        if x < self.n:
            self.hasAsg[x] = True
            self.asg[x] = v

    # push every tag on the root-to-leaf path of leaf p down one level
    def _push(self, p):
        for s in range(self.h, 0, -1):
            x = p >> s
            k = 1 << (s - 1)
            if self.hasAsg[x]:
                self._applyAssign(2 * x, k, self.asg[x])
                self._applyAssign(2 * x + 1, k, self.asg[x])
                self.hasAsg[x] = False

    # recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    def _rebuild(self, p):
        k = 1
        while p > 1:
            p >>= 1
            k <<= 1
            if self.hasAsg[p]:
                v = self.asg[p]
                self.sm[p] = v * k
                self.mn[p] = self.mx[p] = v
                continue
            self.sm[p] = self.sm[2 * p] + self.sm[2 * p + 1]
            self.mn[p] = min(self.mn[2 * p], self.mn[2 * p + 1])
            self.mx[p] = max(self.mx[2 * p], self.mx[2 * p + 1])

    # O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        lo, hi, k = l0, r0 + 1, 1
        while lo < hi:
            if lo & 1:
                self._applyAssign(lo, k, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._applyAssign(hi, k, v)
            lo >>= 1
            hi >>= 1
            k <<= 1
        self._rebuild(l0)
        self._rebuild(r0)

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(N) -- the whole array: push every tag down one level at a time from the root (the nodes s levels above
    # the leaves are (n >> s) .. ((2n - 1) >> s); their children cover k = 1 << (s - 1) leaves), then read the leaves
    def getAll(self):
        n = self.n
        for s in range(self.h, 0, -1):
            k = 1 << (s - 1)
            for x in range(max(1, n >> s), ((2 * n - 1) >> s) + 1):
                if self.hasAsg[x]:
                    self._applyAssign(2 * x, k, self.asg[x])
                    self._applyAssign(2 * x + 1, k, self.asg[x])
                    self.hasAsg[x] = False
        return self.sm[n:]

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        return self.sm[p]

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        self.sm[p] = self.mn[p] = self.mx[p] = val
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
