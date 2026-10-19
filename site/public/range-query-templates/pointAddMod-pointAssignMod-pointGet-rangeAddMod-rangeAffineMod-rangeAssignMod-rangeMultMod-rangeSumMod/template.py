# @operations: pointAddMod pointAssignMod pointGet rangeAddMod rangeAffineMod rangeAssignMod rangeMultMod rangeSumMod
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAddMod: log(N)
#   pointAssignMod: log(N)
#   pointGet: log(N)
#   rangeAddMod: log(N)
#   rangeAffineMod: log(N)
#   rangeAssignMod: log(N)
#   rangeMultMod: log(N)
#   rangeSumMod: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: tot[2*N]
#   tags: mul[1*N] add[1*N]
#   other: none
#   note: tags live on the N internal nodes only; each is one affine map x -> x*mul + add (mod p)

# Range affine (a[i] = a[i] * mult + add), add, mult, assign, and range sum, all mod p, plus point ops.
# All indices 0-based, ranges inclusive [l, r]. Every update is one affine tag (mult, add):
#   add x -> (1, x)   mult m -> (m, 0)   assign x -> (0, x)
# Composing f = (m1, a1) then g = (m2, a2) gives (m1 * m2, a1 * m2 + a2): the OLD add is scaled by the NEW mult.
# Iterative 2N lazy tree: values on the leaves, a tag on each internal node ("applied here, not yet pushed"). A
# covering node at level s is a perfect subtree of 2^s leaves, so v -> v * m + a turns its sum into sum * m + a * 2^s.


class AffineSumTree:
    __slots__ = ("n", "h", "mod", "tot", "mul", "add")

    # O(N)
    def __init__(self, arr, mod=1000000007):
        self.mod = mod
        n = self.n = len(arr)
        self.h = n.bit_length()
        tot = self.tot = [0] * n + [v % mod for v in arr]
        for x in range(n - 1, 0, -1):
            tot[x] = (tot[2 * x] + tot[2 * x + 1]) % mod
        self.mul = [1] * n  # tags on internal nodes only
        self.add = [0] * n

    # v -> v * m + a on node x, which covers k slots
    def _apply(self, x, k, m, a):
        mod = self.mod
        self.tot[x] = (self.tot[x] * m + a * k) % mod
        if x < self.n:
            self.mul[x] = self.mul[x] * m % mod
            self.add[x] = (self.add[x] * m + a) % mod

    # push every tag on the root-to-leaf path of leaf p down one level
    def _push(self, p):
        for s in range(self.h, 0, -1):
            x = p >> s
            if self.mul[x] != 1 or self.add[x]:
                k = 1 << (s - 1)
                self._apply(2 * x, k, self.mul[x], self.add[x])
                self._apply(2 * x + 1, k, self.mul[x], self.add[x])
                self.mul[x] = 1
                self.add[x] = 0

    # recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    def _rebuild(self, p):
        tot, mod, k = self.tot, self.mod, 1
        while p > 1:
            p >>= 1
            k <<= 1
            tot[p] = ((tot[2 * p] + tot[2 * p + 1]) * self.mul[p] + self.add[p] * k) % mod

    def _update(self, l, r, m, a):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        i, j, k = l0, r0 + 1, 1
        while i < j:
            if i & 1:
                self._apply(i, k, m, a)
                i += 1
            if j & 1:
                j -= 1
                self._apply(j, k, m, a)
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

    # O(logN) -- a[i] = a[i] * mult + add (mod p) for i in [l, r]; every other update is this one
    def rangeAffineMod(self, l, r, mult, add):
        self._update(l, r, mult % self.mod, add % self.mod)

    # O(logN) -- a[i] += v (mod p) for i in [l, r]
    def rangeAddMod(self, l, r, v):
        self._update(l, r, 1, v % self.mod)

    # O(logN) -- a[i] *= m (mod p) for i in [l, r]
    def rangeMultMod(self, l, r, m):
        self._update(l, r, m % self.mod, 0)

    # O(logN) -- a[i] = v for i in [l, r]: multiply by 0, then add v
    def rangeAssignMod(self, l, r, v):
        self._update(l, r, 0, v % self.mod)

    # O(logN) -- a[i] = val (mod p)
    def pointAssignMod(self, i, val):
        self._update(i, i, 0, val % self.mod)

    # O(logN) -- a[i] += delta (mod p)
    def pointAddMod(self, i, delta):
        self._update(i, i, 1, delta % self.mod)
