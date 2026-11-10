# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/rangeSum/template.py
# @operations: rangeSum sumAll
# @data-structure-type: prefix-sum
# @complexities:
#   rangeSum: 1
#   sumAll: 1
#   build: N
# @memory:
#   layout: none
#   node: P[1*N]
#   tags: none
#   other: none
#   note: P[i] = a[0] + ... + a[i-1], one more entry than the array

# Static range sum with a prefix sum array: O(N) build, O(1) per query, no updates. All indices 0-based, ranges
# inclusive [l, r].


class PrefixSums:
    __slots__ = ("n", "P")

    # O(N) -- arr: the array (a list, can be empty)
    def __init__(self, arr):
        self.n = len(arr)
        P = self.P = [0] * (self.n + 1)
        for i, v in enumerate(arr):
            P[i + 1] = P[i] + v

    # O(1) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self.P[r + 1] - self.P[l]

    # O(1) -- a[0] + ... + a[n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.P[self.n]
