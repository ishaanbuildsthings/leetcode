# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/doAllElementsAppearEvenFrequency-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/template.py
# @operations: doAllElementsAppearEvenFrequency getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
# @data-structure-type: lazy-seg-tree
# @letters: same
# @complexities:
#   doAllElementsAppearEvenFrequency: log(N)
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAssign: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: xr[2*N]
#   tags: asg[1*N] hasAsg[1*N]
#   other: vals[1*N]
#   note: xr holds the xor of value tags; a value's tag is splitmix64(value ^ seed), a keyed hash with a random per-run seed, so there is no value -> tag table; vals holds each leaf's value

from random import getrandbits

MASK = (1 << 64) - 1

# Range "does every value appear an even number of times?" via xor hashing, with range assign. All indices 0-based,
# ranges inclusive [l, r].
# Each distinct value gets a 64-bit tag, splitmix64(value ^ seed): a bijection on 64-bit ints keyed by a random per-run
# seed, so equal values share a tag and distinct integers never collide. Xor over a range cancels tags in pairs, so an
# all-even range hashes to 0; false positives (unequal tags whose xor cancels) have probability ~q / 2^64.
# Lazy segment tree (2N iterative) over the tags: a node assigned value v holds tag(v) if it covers an odd number of
# leaves, else 0. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its
# level), and every internal node holds its pending assign: an update pushes the tags on its two boundary leaf paths,
# tags the covering nodes, then rebuilds both paths.


class XorEvenAssign:
    __slots__ = ("n", "h", "seed", "xr", "vals", "asg", "hasAsg")

    # O(N) -- arr: the initial array; values may be any hashable type
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.seed = getrandbits(64)
        self.vals = list(arr)
        self.xr = [0] * n + [self._tagOf(v) for v in arr]
        self.asg = [None] * n
        self.hasAsg = [0] * n
        xr = self.xr
        for x in range(n - 1, 0, -1):
            xr[x] = xr[2 * x] ^ xr[2 * x + 1]

    # O(1) -- the value's tag: splitmix64(v ^ seed). Ints are used as-is (hash(-1) == hash(-2) in CPython)
    def _tagOf(self, v):
        z = ((v if type(v) is int else hash(v)) & MASK) ^ self.seed
        z = (z + 0x9E3779B97F4A7C15) & MASK
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        return z ^ (z >> 31)

    # O(logN) -- True iff every value in a[l..r] occurs an even number of times; needs 0 <= l <= r < n, else IndexError
    def doAllElementsAppearEvenFrequency(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"doAllElementsAppearEvenFrequency: needs 0 <= l <= r < n, got "
                             f"l = {l}, r = {r}, n = {self.n}")
        n, xr = self.n, self.xr
        self._pushPath(l + n)
        self._pushPath(r + n)
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res ^= xr[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res ^= xr[hi]
            lo >>= 1
            hi >>= 1
        return res == 0

    # O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, t = self.n, self._tagOf(v)
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi = l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                self._apply(lo, v, t)
                lo += 1
            if hi & 1:
                hi -= 1
                self._apply(hi, v, t)
            lo >>= 1
            hi >>= 1
        self._rebuild(l + n)
        self._rebuild(r + n)

    # O(logN) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        self.vals[i], self.xr[p] = v, self._tagOf(v)
        self._rebuild(p)

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self._pushPath(i + self.n)
        return self.vals[i]

    # O(N) -- the whole array, every pending assign pushed down on the way
    def getAll(self):
        n = self.n
        for x in range(1, n):  # (parents before children)
            self._push(x)
        return list(self.vals)

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if v > self.pointGet(i):
            self.pointAssign(i, v)

    # O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if v < self.pointGet(i):
            self.pointAssign(i, v)

    # ---- internals ----

    def _apply(self, x, v, t):  # every value under node x becomes v, whose tag is t
        if x >= self.n:
            self.vals[x - self.n], self.xr[x] = v, t
        else:
            self.xr[x] = 0  # (an assigned internal node is a perfect subtree of 2^s >= 2 leaves: an even count)
            self.asg[x], self.hasAsg[x] = v, 1

    def _push(self, x):  # hand node x's pending assign to its children
        if self.hasAsg[x]:
            v = self.asg[x]
            t = self._tagOf(v)
            self._apply(2 * x, v, t)
            self._apply(2 * x + 1, v, t)
            self.hasAsg[x] = 0

    def _pushPath(self, p):  # hand down every pending assign on the path from the root to leaf p
        for s in range(self.h, 0, -1):
            self._push(p >> s)

    def _rebuild(self, p):  # recompute every ancestor of leaf p (an assigned node keeps its own value)
        xr, hasAsg = self.xr, self.hasAsg
        while p > 1:
            p >>= 1
            if not hasAsg[p]:
                xr[p] = xr[2 * p] ^ xr[2 * p + 1]
