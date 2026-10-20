# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeOrApply-rangeOrQuery-rangeSum-rangeXorApply/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeOrApply rangeOrQuery rangeSum rangeXorApply
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(N)*log(U)
#   pointAssign: log(N)*log(U)
#   pointChmax: log(N)*log(U)
#   pointChmin: log(N)*log(U)
#   pointGet: log(N)*log(U)
#   rangeAndApply: log(N)*log(U)
#   rangeAndQuery: log(N)*log(U)
#   rangeOrApply: log(N)*log(U)
#   rangeOrQuery: log(N)*log(U)
#   rangeSum: log(N)*log(U)
#   rangeXorApply: log(N)*log(U)
#   build: N*log(U)
# @memory:
#   layout: 2n-iterative
#   node: cnt[2*N*log(U)]
#   tags: andTag[1*N] xorTag[1*N]
#   other: none
#   note: cnt keeps, per node and per bit, how many values below have that bit set (bits = log U, 20 by default); tags live on internal nodes only

# Range and= / or= / xor= with range sum / and / or queries, plus point ops. All indices 0-based, ranges inclusive.
# Values live in [0, 2^bits). Each node counts, for every bit, how many of its values have that bit set. Every
# update is v -> (v & a) ^ x (and X = (X, 0), or X = (~X, X), xor X = (FULL, X)), and per bit that is "keep",
# "force 0", "force 1" or "flip": force sets the count to 0 or the node length, flip turns c into length - c.
# So every update is an ordinary lazy tag, a true O(log N * bits) with no amortization (unlike bitwise beats,
# which cannot apply xor to a node whose values disagree on a bit). Sum = sum over bits of count * 2^bit.
# Iterative 2N lazy tree; a covering node at level s is a perfect subtree of 2^s leaves.


class BitCountTree:
    __slots__ = ("n", "h", "bits", "full", "cnt", "andTag", "xorTag")

    # O(N * bits)
    def __init__(self, arr, bits=20):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.bits = bits
        full = self.full = (1 << bits) - 1
        cnt = self.cnt = [[0] * (2 * n) for _ in range(bits)]  # cnt[b][x] = # of values under node x with bit b set
        for i, v in enumerate(arr):
            for b in range(bits):
                if v >> b & 1:
                    cnt[b][n + i] = 1
        for c in cnt:
            for x in range(n - 1, 0, -1):
                c[x] = c[2 * x] + c[2 * x + 1]
        self.andTag = [full] * n  # tags on internal nodes only
        self.xorTag = [0] * n

    # v -> (v & a) ^ xr on node x, which covers k slots
    def _apply(self, x, k, a, xr):
        for b in range(self.bits):
            c = self.cnt[b]
            if not a >> b & 1:
                c[x] = 0
            if xr >> b & 1:
                c[x] = k - c[x]
        if x < self.n:
            self.andTag[x] &= a
            self.xorTag[x] = (self.xorTag[x] & a) ^ xr

    def _push(self, p):
        full = self.full
        for s in range(self.h, 0, -1):
            x = p >> s
            a, xr = self.andTag[x], self.xorTag[x]
            if a != full or xr:
                k = 1 << (s - 1)
                self._apply(2 * x, k, a, xr)
                self._apply(2 * x + 1, k, a, xr)
                self.andTag[x], self.xorTag[x] = full, 0

    def _rebuild(self, p):
        k = 1
        while p > 1:
            p >>= 1
            k <<= 1
            a, xr = self.andTag[p], self.xorTag[p]
            for b in range(self.bits):
                c = self.cnt[b]
                v = c[2 * p] + c[2 * p + 1]
                if not a >> b & 1:
                    v = 0
                if xr >> b & 1:
                    v = k - v
                c[p] = v

    def _update(self, l, r, a, xr):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        i, j, k = l0, r0 + 1, 1
        while i < j:
            if i & 1:
                self._apply(i, k, a, xr)
                i += 1
            if j & 1:
                j -= 1
                self._apply(j, k, a, xr)
            i >>= 1
            j >>= 1
            k <<= 1
        self._rebuild(l0)
        self._rebuild(r0)

    # the canonical nodes of [l, r] with their lengths, after pushing the two boundary paths
    def _nodes(self, l, r):
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        out, k = [], 1
        r += 1
        while l < r:
            if l & 1:
                out.append((l, k))
                l += 1
            if r & 1:
                r -= 1
                out.append((r, k))
            l >>= 1
            r >>= 1
            k <<= 1
        return out

    # O(logN * bits) -- a[i] &= X for i in [l, r]
    def rangeAndApply(self, l, r, X):
        self._update(l, r, X & self.full, 0)

    # O(logN * bits) -- a[i] |= X for i in [l, r]
    def rangeOrApply(self, l, r, X):
        self._update(l, r, ~X & self.full, X & self.full)

    # O(logN * bits) -- a[i] ^= X for i in [l, r]
    def rangeXorApply(self, l, r, X):
        self._update(l, r, self.full, X & self.full)

    # O(logN * bits) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        if l > r:
            return 0
        nodes = self._nodes(l, r)
        return sum(sum(self.cnt[b][x] for x, _ in nodes) << b for b in range(self.bits))

    # O(logN * bits) -- a[l] & ... & a[r]
    def rangeAndQuery(self, l, r):
        nodes = self._nodes(l, r)
        return sum(1 << b for b in range(self.bits) if all(self.cnt[b][x] == k for x, k in nodes))

    # O(logN * bits) -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r):
        nodes = self._nodes(l, r)
        return sum(1 << b for b in range(self.bits) if any(self.cnt[b][x] for x, _ in nodes))

    # O(logN * bits) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        self._push(p)
        return sum(self.cnt[b][p] << b for b in range(self.bits))

    # O(logN * bits) -- a[i] = val & FULL
    def pointAssign(self, i, val):
        p = i + self.n
        self._push(p)
        val &= self.full
        for b in range(self.bits):
            self.cnt[b][p] = val >> b & 1
        self._rebuild(p)

    # O(logN * bits) -- a[i] = (a[i] + delta) & FULL
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logN * bits) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logN * bits) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
