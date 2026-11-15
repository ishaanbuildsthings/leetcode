# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sparse-table-and-or/template.py
# @operations: andAll orAll pointGet rangeAndQuery rangeOrQuery
# @data-structure-type: sparse-table
# @complexities:
#   pointGet: 1
#   rangeAndQuery: 1
#   rangeOrQuery: 1
#   andAll: 1
#   orAll: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: an[1*N*log(N)] orr[1*N*log(N)]
#   tags: none
#   other: none
#   note: one table per aggregate (AND, OR), each log(N) levels of up to N values; level 0 is the array itself

# Static range AND and OR in one class: one sparse table per aggregate. Level k of a table holds that aggregate of every
# window of 2^k values, and a range is the combine of the two largest power-of-two windows that fit, one starting at l
# and one ending at r (they overlap, which is fine: each of these gives the same answer when a value is counted twice).
# No updates. All indices 0-based, ranges inclusive.


class SparseAndOr:
    # O(N log N) -- arr: the array (a list)
    def __init__(self, arr):
        self.n = n = len(arr)
        # an[k][i]: the AND of arr[i .. i + 2^k - 1]
        self.an = t = [list(arr)]
        half = 1
        while 2 * half <= n:
            prev = t[-1]
            t.append([a & b for a, b in zip(prev, prev[half:])])
            half *= 2
        # orr[k][i]: the OR of arr[i .. i + 2^k - 1]
        self.orr = t = [list(arr)]
        half = 1
        while 2 * half <= n:
            prev = t[-1]
            t.append([a | b for a, b in zip(prev, prev[half:])])
            half *= 2

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.an[0][i]

    # O(1) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeAndQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAndQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        k = (r - l + 1).bit_length() - 1
        row = self.an[k]
        a, b = row[l], row[r - (1 << k) + 1]
        return a & b

    # O(1) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeOrQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeOrQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        k = (r - l + 1).bit_length() - 1
        row = self.orr[k]
        a, b = row[l], row[r - (1 << k) + 1]
        return a | b

    # O(1) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def andAll(self):
        if self.n < 1:
            raise IndexError("andAll: needs n >= 1")
        return self.rangeAndQuery(0, self.n - 1)

    # O(1) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def orAll(self):
        if self.n < 1:
            raise IndexError("orAll: needs n >= 1")
        return self.rangeOrQuery(0, self.n - 1)
