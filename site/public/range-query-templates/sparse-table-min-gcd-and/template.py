# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sparse-table-min-gcd-and/template.py
# @operations: andAll gcdAll minAll pointGet rangeAndQuery rangeGcd rangeMin
# @data-structure-type: sparse-table
# @complexities:
#   pointGet: 1
#   rangeAndQuery: 1
#   rangeGcd: log(U) ?
#   rangeMin: 1
#   minAll: 1
#   gcdAll: log(U) ?
#   andAll: 1
#   build: N*log(N)*log(U) ?
# @memory:
#   layout: none
#   node: mn[1*N*log(N)] g[1*N*log(N)] an[1*N*log(N)]
#   tags: none
#   other: none
#   note: one table per aggregate (min, gcd, AND), each log(N) levels of up to N values; level 0 is the array itself

# Static range min, gcd and AND in one class: one sparse table per aggregate. Level k of a table holds that aggregate
# of every window of 2^k values, and a range is the combine of the two largest power-of-two windows that fit, one
# starting at l and one ending at r (they overlap, which is fine: each of these gives the same answer when a value is
# counted twice). No updates. All indices 0-based, ranges inclusive. A gcd is a Euclid run, O(log U), so rangeGcd
# costs one of those and the build N log N of them.
from math import gcd


class SparseMinGcdAnd:
    # O(N log N) -- arr: the array (a list)
    def __init__(self, arr):
        self.n = n = len(arr)
        # mn[k][i]: the min of arr[i .. i + 2^k - 1]
        self.mn = t = [list(arr)]
        half = 1
        while 2 * half <= n:
            prev = t[-1]
            t.append([a if a < b else b for a, b in zip(prev, prev[half:])])
            half *= 2
        # g[k][i]: the gcd of arr[i .. i + 2^k - 1]
        self.g = t = [list(arr)]
        half = 1
        while 2 * half <= n:
            prev = t[-1]
            t.append([gcd(a, b) for a, b in zip(prev, prev[half:])])
            half *= 2
        # an[k][i]: the AND of arr[i .. i + 2^k - 1]
        self.an = t = [list(arr)]
        half = 1
        while 2 * half <= n:
            prev = t[-1]
            t.append([a & b for a, b in zip(prev, prev[half:])])
            half *= 2

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.mn[0][i]

    # O(1) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        k = (r - l + 1).bit_length() - 1
        row = self.mn[k]
        a, b = row[l], row[r - (1 << k) + 1]
        return a if a < b else b

    # O(log U) -- gcd of |a[l]|, ..., |a[r]| (0 only if all are 0); needs 0 <= l <= r < n, else IndexError
    def rangeGcd(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeGcd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        k = (r - l + 1).bit_length() - 1
        row = self.g[k]
        a, b = row[l], row[r - (1 << k) + 1]
        return gcd(a, b)

    # O(1) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeAndQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAndQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        k = (r - l + 1).bit_length() - 1
        row = self.an[k]
        a, b = row[l], row[r - (1 << k) + 1]
        return a & b

    # O(1) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.n < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.n - 1)

    # O(log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else raises IndexError
    def gcdAll(self):
        if self.n < 1:
            raise IndexError("gcdAll: needs n >= 1")
        return self.rangeGcd(0, self.n - 1)

    # O(1) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def andAll(self):
        if self.n < 1:
            raise IndexError("andAll: needs n >= 1")
        return self.rangeAndQuery(0, self.n - 1)
