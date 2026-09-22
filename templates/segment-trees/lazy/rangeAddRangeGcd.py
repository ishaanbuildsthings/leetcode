# TEMPLATE BY https://github.com/agrawalishaan

# ========================
# COMPLEXITIES

# O(n) build time, O(n) memory

# O(log n * log maxVal) rangeAdd(l, r, x)
# O(log n) pointQuery(i) -> value
# O(log n + log maxVal) rangeGcd(l, r) -> gcd

# ========================
"""
How does range add + range gcd work?

The gcd of a group of numbers doesn't change if we swap every number except one for its difference with a neighbor.
Think of each number as a node and each adjacent difference as an edge. Starting from one real value (the anchor),
walking an edge only adds a known difference, so anything dividing the anchor and every edge divides every number
we reach. The adjacent differences form a chain touching every node, so the gcd of a range is the first value in the
range gcd'd with the differences strictly inside the range. The difference entering the range connects to a number
outside it and must not be used.

Adding x to a whole range leaves every difference inside it unchanged. Only two differences move: the one entering
the range goes up by x, and the one leaving it goes down by x. So a range add is two point changes on the difference
array.

We keep that one difference array in two structures:
-a Fenwick tree, since summing the differences up to a position gives the real value there (the anchor)
-a gcd segment tree, for the gcd of the differences inside a range

Example: [6, 10, 14, 22, 30], differences [_, 4, 4, 8, 8]
rangeGcd(1, 3) = gcd(10, 4, 8) = 2 (anchor 10, then the two differences inside, never the 4 entering at index 1)
"""

# ========================


from math import gcd


class RangeAddRangeGcd:
    __slots__ = ("n", "diff", "fen", "seg")

    # O(n)
    def __init__(self, arr):
        self.n = n = len(arr)

        self.diff = diff = [arr[0]] + [arr[i] - arr[i - 1] for i in range(1, n)]

        self.fen = fen = [0] + diff[:]
        for i in range(1, n + 1):
            parent = i + (i & -i)
            if parent <= n:
                fen[parent] += fen[i]

        # leaf 0 stays 0 (it holds the anchor in diff, not a real difference)
        self.seg = seg = [0] * (2 * n)
        for i in range(1, n):
            seg[n + i] = abs(diff[i])
        for p in range(n - 1, 0, -1):
            seg[p] = gcd(seg[2 * p], seg[2 * p + 1])

    def _fenAdd(self, i, x):
        fen = self.fen
        n = self.n
        i += 1
        while i <= n:
            fen[i] += x
            i += i & -i

    def _fenPrefix(self, i):
        fen = self.fen
        total = 0
        i += 1
        while i > 0:
            total += fen[i]
            i -= i & -i
        return total

    def _segSet(self, i, val):
        seg = self.seg
        p = i + self.n
        seg[p] = val
        p >>= 1
        while p:
            seg[p] = gcd(seg[2 * p], seg[2 * p + 1])
            p >>= 1

    def _segQuery(self, l, r):
        seg = self.seg
        res = 0
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                res = gcd(res, seg[l])
                l += 1
            if r & 1:
                r -= 1
                res = gcd(res, seg[r])
            l >>= 1
            r >>= 1
        return res

    def _shiftDiff(self, i, x):
        self.diff[i] += x
        self._fenAdd(i, x)
        if i >= 1:
            self._segSet(i, abs(self.diff[i]))

    #################### PUBLIC METHODS START HERE ####################

    # O(log n * log maxVal) -- adds x to every arr[l...r] inclusive. requires 0 <= l <= r < n, x may be negative
    def rangeAdd(self, l, r, x):
        self._shiftDiff(l, x)
        if r + 1 < self.n:
            self._shiftDiff(r + 1, -x)

    # O(log n) -- current value of arr[i]
    def pointQuery(self, i):
        return self._fenPrefix(i)

    # O(log n + log maxVal) -- gcd of arr[l...r] inclusive, always >= 0. requires 0 <= l <= r < n
    # returns 0 only if every value in the range is 0
    def rangeGcd(self, l, r):
        res = abs(self._fenPrefix(l))
        if l < r:
            res = gcd(res, self._segQuery(l + 1, r))
        return res


# EXAMPLE IN USE:
# Row GCD (CF 1458A): gcd(a[0] + b, a[1] + b, ...) for each b
# rg = RangeAddRangeGcd(a)
# for b in bs:
#     rg.rangeAdd(0, n - 1, b)
#     print(rg.rangeGcd(0, n - 1))
#     rg.rangeAdd(0, n - 1, -b)