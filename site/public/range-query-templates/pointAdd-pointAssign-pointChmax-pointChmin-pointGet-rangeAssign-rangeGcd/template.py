# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeGcd
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(N)*log(U) ?
#   pointAssign: log(N)*log(U) ?
#   pointChmax: log(N)*log(U) ?
#   pointChmin: log(N)*log(U) ?
#   pointGet: log(N)
#   rangeAssign: log(N)*log(U) ?
#   rangeGcd: log(N)+log(U) ?
#   build: N*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: t[2*N]
#   tags: asg[1*N] hasAsg[1*N]
#   other: none
#   note: leaves t[n..2n) hold the values, internal nodes the gcd of |values| below; tags live on internal nodes only

from math import gcd

# Range assign + range gcd, plus point ops. All indices 0-based, ranges inclusive [l, r]. Gcds are of |values|.
# Iterative 2N lazy tree: leaves hold the values, internal nodes the gcd below them, and a pending assign on each
# internal node ("applied here, not yet pushed"). A node assigned v has gcd |v|, so assign is an ordinary lazy tag.
# Much lighter than the gcd beats tree when you only need assign.


class AssignGcdTree:
    __slots__ = ("n", "h", "t", "asg", "hasAsg")

    # O(N logU)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        t = self.t = [0] * n + list(arr)
        for x in range(n - 1, 0, -1):
            t[x] = gcd(t[2 * x], t[2 * x + 1])
        self.asg = [0] * n  # tags on internal nodes only
        self.hasAsg = [False] * n

    def _apply(self, x, v):
        if x < self.n:
            self.t[x] = abs(v)
            self.hasAsg[x] = True
            self.asg[x] = v
        else:
            self.t[x] = v

    def _push(self, p):
        for s in range(self.h, 0, -1):
            x = p >> s
            if self.hasAsg[x]:
                self._apply(2 * x, self.asg[x])
                self._apply(2 * x + 1, self.asg[x])
                self.hasAsg[x] = False

    def _rebuild(self, p):
        t = self.t
        while p > 1:
            p >>= 1
            t[p] = abs(self.asg[p]) if self.hasAsg[p] else gcd(t[2 * p], t[2 * p + 1])

    # O(logN logU) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        i, j = l0, r0 + 1
        while i < j:
            if i & 1:
                self._apply(i, v)
                i += 1
            if j & 1:
                j -= 1
                self._apply(j, v)
            i >>= 1
            j >>= 1
        self._rebuild(l0)
        self._rebuild(r0)

    # O(logN + logU) -- gcd of |a[l]|, ..., |a[r]| (the gcds telescope, so the fold costs one log U)
    def rangeGcd(self, l, r):
        if l > r:
            return 0
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        t, res = self.t, 0
        r += 1
        while l < r:
            if l & 1:
                res = gcd(res, t[l])
                l += 1
            if r & 1:
                r -= 1
                res = gcd(res, t[r])
            l >>= 1
            r >>= 1
        return res

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        self._push(p)
        return self.t[p]

    # O(logN logU) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAssign(i, i, val)

    # O(logN logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAssign(i, i, self.pointGet(i) + delta)

    # O(logN logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.rangeAssign(i, i, val)

    # O(logN logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.rangeAssign(i, i, val)
