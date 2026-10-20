# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/doAllElementsAppearEvenFrequency-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/template.py
# @operations: doAllElementsAppearEvenFrequency pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: BIT
# @complexities:
#   doAllElementsAppearEvenFrequency: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   build: N
# @memory:
#   layout: none
#   node: bit[1*N]
#   tags: none
#   other: vals[1*N] a[1*N]
#   note: a holds each index's tag; a value's tag is splitmix64(value ^ seed), a keyed hash with a random per-run seed, so there is no value -> tag table
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/xorHashing_allEven_withUpdates.py

from random import getrandbits

MASK = (1 << 64) - 1


class XorEven:
    # Range "is every value's count even?" via XOR hashing.
    # Each distinct value gets a 64-bit tag, splitmix64(value ^ seed): a bijection on 64-bit ints keyed by a
    # random per-run seed, so equal values share a tag, distinct ints never collide, and no table is needed.
    # XOR over a range cancels tags
    # in pairs, so an all-even range hashes to 0. False positives (nonzero counts
    # that happen to cancel) have probability ~q/2^64.
    # XOR is invertible, so a Fenwick tree suffices — no segment tree needed.
    # Values may be any hashable type. O(n) build, O(log n) update, O(log n) query.
    # All indices 0-based, all ranges inclusive.
    def __init__(self, arr):
        self.vals = list(arr)
        self.n = n = len(arr)
        self.seed = getrandbits(64)
        self.a = [self._tagOf(v) for v in arr]
        # O(n) build: seed the tree, then push each node into its parent
        bit = [0] * (n + 1)
        for i in range(n):
            bit[i + 1] = self.a[i]
        for i in range(1, n + 1):
            j = i + (i & -i)
            if j <= n:
                bit[j] ^= bit[i]
        self.bit = bit

    # O(1) — the value's tag: splitmix64(v ^ seed). Ints are used as-is (hash(-1) == hash(-2) in CPython)
    def _tagOf(self, v):
        z = ((v if type(v) is int else hash(v)) & MASK) ^ self.seed
        z = (z + 0x9E3779B97F4A7C15) & MASK
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        return z ^ (z >> 31)

    # O(log n) — assign position i the value val (overwrite, not add)
    def pointAssign(self, i, val):
        self.vals[i] = val
        t = self._tagOf(val)
        d = self.a[i] ^ t
        if not d:
            return
        self.a[i] = t
        bit, n = self.bit, self.n
        p = i + 1
        while p <= n:
            bit[p] ^= d
            p += p & -p

    # O(log n) — XOR of tags over [0, i]; i may be -1
    def prefix(self, i):
        s = 0
        bit = self.bit
        p = i + 1
        while p > 0:
            s ^= bit[p]
            p -= p & -p
        return s

    # O(log n) — XOR of tags over [l, r]
    def rangeXor(self, l, r):
        return self.prefix(r) ^ (self.prefix(l - 1) if l else 0)

    # O(log n) — True iff every value in a[l..r] occurs an even number of times
    def doAllElementsAppearEvenFrequency(self, l, r):
        return self.rangeXor(l, r) == 0

    # O(log n) — True iff exactly one value occurs an odd number of times in
    # a[l..r], and that value is val (the classic "all even except one" check)
    def oneOdd(self, l, r, val):
        return self.rangeXor(l, r) == self._tagOf(val)

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.vals[i]

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.vals[i]:
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.vals[i]:
            self.pointAssign(i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.vals[i] + delta)