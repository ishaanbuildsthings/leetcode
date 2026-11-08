# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndQuery-rangeOrQuery-rangeSum-rangeXorApply/template.py
# @operations: andAll getAll orAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeOrQuery rangeSum rangeXorApply sumAll
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N*log(U)
#   pointAdd: log(N)*log(U)
#   pointAssign: log(N)*log(U)
#   pointChmax: log(N)*log(U)
#   pointChmin: log(N)*log(U)
#   pointGet: log(N)*log(U)
#   rangeAndQuery: log(N)*log(U)
#   rangeOrQuery: log(N)*log(U)
#   rangeSum: log(N)*log(U)
#   rangeXorApply: log(N)*log(U)
#   sumAll: log(N)*log(U)
#   andAll: log(N)*log(U)
#   orAll: log(N)*log(U)
#   build: N*log(U)
# @memory:
#   layout: 2n-iterative
#   node: cnt[2*N*log(U)]
#   tags: xorTag[1*N]
#   other: none
#   note: cnt keeps, per node and per bit, how many values below have that bit set (bits = log U, 20 by default); tags live on internal nodes only

# Range xor= with range sum / and / or queries, plus point ops. All indices 0-based, ranges inclusive.
# Values live in [0, 2^bits). Each node counts, for every bit, how many of its values have that bit set. A xor X
# flips the bits set in X: per bit, a flip turns the count c into length - c, so the tag is just the mask to
# flip (this is BitCountTree without the AND tag that only and= / or= need).
# So every update is an ordinary lazy tag, a true O(log N * bits) with no amortization (unlike bitwise beats,
# which cannot apply xor to a node whose values disagree on a bit). Sum = sum over bits of count * 2^bit.
# Iterative 2N lazy tree; a covering node at level s is a perfect subtree of 2^s leaves.


class BitCountTree:
    __slots__ = ("n", "h", "bits", "full", "cnt", "xorTag")

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
        self.xorTag = [0] * n  # tags on internal nodes only

    # v -> v ^ xr on node x, which covers k slots
    def _apply(self, x, k, xr):
        for b in range(self.bits):
            c = self.cnt[b]
            if xr >> b & 1:
                c[x] = k - c[x]
        if x < self.n:
            self.xorTag[x] ^= xr

    def _push(self, p):
        full = self.full
        for s in range(self.h, 0, -1):
            x = p >> s
            xr = self.xorTag[x]
            if xr:
                k = 1 << (s - 1)
                self._apply(2 * x, k, xr)
                self._apply(2 * x + 1, k, xr)
                self.xorTag[x] = 0

    def _rebuild(self, p):
        k = 1
        while p > 1:
            p >>= 1
            k <<= 1
            xr = self.xorTag[p]
            for b in range(self.bits):
                c = self.cnt[b]
                v = c[2 * p] + c[2 * p + 1]
                if xr >> b & 1:
                    v = k - v
                c[p] = v

    def _update(self, l, r, xr):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        i, j, k = l0, r0 + 1, 1
        while i < j:
            if i & 1:
                self._apply(i, k, xr)
                i += 1
            if j & 1:
                j -= 1
                self._apply(j, k, xr)
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

    # O(logN * bits) -- a[i] ^= X for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeXorApply(self, l, r, X):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeXorApply: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, X & self.full)

    # O(logN * bits) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return 0
        nodes = self._nodes(l, r)
        return sum(sum(self.cnt[b][x] for x, _ in nodes) << b for b in range(self.bits))

    # O(logN * bits) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeAndQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAndQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        nodes = self._nodes(l, r)
        return sum(1 << b for b in range(self.bits) if all(self.cnt[b][x] == k for x, k in nodes))

    # O(logN * bits) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeOrQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeOrQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        nodes = self._nodes(l, r)
        return sum(1 << b for b in range(self.bits) if any(self.cnt[b][x] for x, _ in nodes))

    # O(logN * bits) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        return sum(self.cnt[b][p] << b for b in range(self.bits))

    # O(N) -- the whole array: push every tag down one level at a time from the root (the nodes s levels above
    # the leaves are (n >> s) .. ((2n - 1) >> s); their children cover k = 1 << (s - 1) leaves), then read the leaves
    def getAll(self):
        n, full = self.n, self.full
        for s in range(self.h, 0, -1):
            k = 1 << (s - 1)
            for x in range(max(1, n >> s), ((2 * n - 1) >> s) + 1):
                xr = self.xorTag[x]
                if xr:
                    self._apply(2 * x, k, xr)
                    self._apply(2 * x + 1, k, xr)
                    self.xorTag[x] = 0
        cnt = self.cnt
        return [sum(cnt[b][p] << b for b in range(self.bits)) for p in range(n, 2 * n)]

    # O(logN * bits) -- a[i] = val & FULL; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        val &= self.full
        for b in range(self.bits):
            self.cnt[b][p] = val >> b & 1
        self._rebuild(p)

    # O(logN * bits) -- a[i] = (a[i] + delta) & FULL; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logN * bits) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logN * bits) -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)

    # O(log(N)*log(U)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)

    # O(log(N)*log(U)) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def andAll(self):
        if self.n < 1:
            raise IndexError("andAll: needs n >= 1")
        return self.rangeAndQuery(0, self.n - 1)

    # O(log(N)*log(U)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def orAll(self):
        if self.n < 1:
            raise IndexError("orAll: needs n >= 1")
        return self.rangeOrQuery(0, self.n - 1)
