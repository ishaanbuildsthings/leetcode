# @operations: pointAdd pointAssign pointGet rangeAddMod rangeAffineMod rangeAssignMod rangeMultMod
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointGet: log(N)
#   rangeAddMod: log(N)
#   rangeAffineMod: log(N)
#   rangeAssignMod: log(N)
#   rangeMultMod: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: val[1*N]
#   tags: M[1*N] K[1*N]
#   other: none
#   note: each internal node holds one pending affine map x -> x * M + K (mod p); val holds the leaf values

# Range add / assign / multiply / affine mod p + point ops, no range aggregates. All indices 0-based, ranges
# inclusive. Every update is an affine map (m, k): x -> m * x + k (mod p):
#   add v -> (1, v)    mult m -> (m, 0)    assign v -> (0, v)    affine (m, b) -> (m, b)
# Affine maps compose but not commutatively, so the paths to l and r are pushed before tagging.
# Values are kept in [0, mod);
class AffineTree:
    __slots__ = ("n", "M", "K", "val", "mod")

    # O(N)
    def __init__(self, arr, mod=10**9 + 7):
        self.mod = mod
        n = self.n = len(arr)
        self.M = [1] * n
        self.K = [0] * n
        self.val = [v % mod for v in arr]

    # apply (m, k) on top of whatever node x already holds
    def _apply(self, x, m, k):
        n, mod = self.n, self.mod
        if x >= n:
            val = self.val
            val[x - n] = (val[x - n] * m + k) % mod
        else:
            M, K = self.M, self.K
            M[x] = M[x] * m % mod
            K[x] = (K[x] * m + k) % mod

    # O(logN) -- push every pending map on leaf p's root-to-leaf path down to its children
    def _push(self, p):
        M, K = self.M, self.K
        apply = self._apply
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            m, k = M[x], K[x]
            if m != 1 or k:
                y = x << 1
                apply(y, m, k)
                apply(y | 1, m, k)
                M[x] = 1
                K[x] = 0

    def _update(self, l, r, m, k):
        n = self.n
        l += n
        r += n
        self._push(l)
        self._push(r)
        r += 1
        apply = self._apply
        while l < r:
            if l & 1:
                apply(l, m, k)
                l += 1
            if r & 1:
                r -= 1
                apply(r, m, k)
            l >>= 1
            r >>= 1

    # O(logN) -- a[i] = a[i] * mult + add (mod p) for i in [l, r]
    def rangeAffineMod(self, l, r, mult, add):
        self._update(l, r, mult % self.mod, add % self.mod)

    # O(logN) -- a[i] = a[i] * m (mod p) for i in [l, r]
    def rangeMultMod(self, l, r, m):
        self._update(l, r, m % self.mod, 0)

    # O(logN) -- a[i] += v (mod p) for i in [l, r]
    def rangeAddMod(self, l, r, v):
        self._update(l, r, 1, v % self.mod)

    # O(logN) -- a[i] = v (mod p) for i in [l, r]
    def rangeAssignMod(self, l, r, v):
        self._update(l, r, 0, v % self.mod)

    # O(logN) -- a[i], in [0, mod): apply ancestors' maps bottom-up (deeper tags are older)
    def pointGet(self, i):
        M, K, mod = self.M, self.K, self.mod
        v = self.val[i]
        p = (i + self.n) >> 1
        while p:
            v = (v * M[p] + K[p]) % mod
            p >>= 1
        return v

    # O(logN) -- a[i] = v (mod p)
    def pointAssign(self, i, v):
        self._push(i + self.n)
        self.val[i] = v % self.mod

    # O(logN) -- a[i] += delta (mod p)
    def pointAdd(self, i, delta):
        self._push(i + self.n)
        self.val[i] = (self.val[i] + delta) % self.mod
