# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeMultMod-rangeSumMod/template.py
# @operations: pointAdd pointAssign pointGet rangeMultMod rangeSumMod
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointGet: log(N)
#   rangeMultMod: log(N)
#   rangeSumMod: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: tot[2*N]
#   tags: mul[1*N]
#   other: none
#   note: tags live on the N internal nodes only; each is a pending multiplier (mod p)

# Range multiply + range sum, all mod p, plus point ops. All indices 0-based, ranges inclusive [l, r].
# One tag per internal node: a pending multiplier ("applied here, not yet pushed"). Multipliers compose by
# multiplying, and v -> v * m turns a node's sum into sum * m. Leaner than the affine tree: one tag instead of two.


class MultSumTree:
    __slots__ = ("n", "h", "mod", "tot", "mul")

    # O(N)
    def __init__(self, arr, mod=1000000007):
        self.mod = mod
        n = self.n = len(arr)
        self.h = n.bit_length()
        tot = self.tot = [0] * n + [v % mod for v in arr]
        for x in range(n - 1, 0, -1):
            tot[x] = (tot[2 * x] + tot[2 * x + 1]) % mod
        self.mul = [1] * n  # tags on internal nodes only

    # v -> v * m on node x (k is unused: a product doesn't care how many slots the node covers)
    def _apply(self, x, k, m):
        mod = self.mod
        self.tot[x] = self.tot[x] * m % mod
        if x < self.n:
            self.mul[x] = self.mul[x] * m % mod

    # push every tag on the root-to-leaf path of leaf p down one level
    def _push(self, p):
        for s in range(self.h, 0, -1):
            x = p >> s
            if self.mul[x] != 1:
                k = 1 << (s - 1)
                self._apply(2 * x, k, self.mul[x])
                self._apply(2 * x + 1, k, self.mul[x])
                self.mul[x] = 1

    # recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    def _rebuild(self, p):
        tot, mod, k = self.tot, self.mod, 1
        while p > 1:
            p >>= 1
            k <<= 1
            tot[p] = (tot[2 * p] + tot[2 * p + 1]) * self.mul[p] % mod

    def _update(self, l, r, m):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        i, j, k = l0, r0 + 1, 1
        while i < j:
            if i & 1:
                self._apply(i, k, m)
                i += 1
            if j & 1:
                j -= 1
                self._apply(j, k, m)
            i >>= 1
            j >>= 1
            k <<= 1
        self._rebuild(l0)
        self._rebuild(r0)

    # O(logN) -- (a[l] + ... + a[r]) mod p
    def rangeSumMod(self, l, r):
        if l > r:
            return 0
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        tot, res = self.tot, 0
        r += 1
        while l < r:
            if l & 1:
                res += tot[l]
                l += 1
            if r & 1:
                r -= 1
                res += tot[r]
            l >>= 1
            r >>= 1
        return res % self.mod

    # O(logN) -- a[i], in [0, mod)
    def pointGet(self, i):
        p = i + self.n
        self._push(p)
        return self.tot[p]

    # O(logN) -- a[i] *= m (mod p) for i in [l, r]
    def rangeMultMod(self, l, r, m):
        self._update(l, r, m % self.mod)

    # O(logN) -- a[i] = val (mod p)
    def pointAssign(self, i, val):
        p = i + self.n
        self._push(p)
        self.tot[p] = val % self.mod
        self._rebuild(p)

    # O(logN) -- a[i] += delta (mod p)
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)
