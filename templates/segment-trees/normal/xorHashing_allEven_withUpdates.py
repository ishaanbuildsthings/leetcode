from random import getrandbits


class XorEven:
    # Range "is every value's count even?" via XOR hashing.
    # Each distinct value gets a random 64-bit tag. XOR over a range cancels tags
    # in pairs, so an all-even range hashes to 0. False positives (nonzero counts
    # that happen to cancel) have probability ~q/2^64.
    # XOR is invertible, so a Fenwick tree suffices — no segment tree needed.
    # Values may be any hashable type. O(n) build, O(log n) update, O(log n) query.
    # All indices 0-based, all ranges inclusive.
    def __init__(self, arr):
        self.n = n = len(arr)
        self.tag = {}
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

    # O(1) amortized — random tag for a value, minted on first sight
    def _tagOf(self, v):
        t = self.tag.get(v)
        if t is None:
            t = self.tag[v] = getrandbits(64)
        return t

    # O(log n) — assign position i the value val (overwrite, not add)
    def pointSet(self, i, val):
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
    def allEven(self, l, r):
        return self.rangeXor(l, r) == 0

    # O(log n) — True iff exactly one value occurs an odd number of times in
    # a[l..r], and that value is val (the classic "all even except one" check)
    def oneOdd(self, l, r, val):
        return self.rangeXor(l, r) == self._tagOf(val)