# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/rangeSumMod/template.py
# @operations: rangeSumMod
# @data-structure-type: prefix-sum
# @complexities:
#   rangeSumMod: 1
#   build: N
# @memory:
#   layout: none
#   node: P[1*N]
#   tags: none
#   other: none
#   note: P[i] = (a[0] + ... + a[i-1]) % MOD, one more entry than the array

# Static range sum % MOD with a prefix sum array: O(N) build, O(1) per query, no updates. All indices 0-based, ranges
# inclusive [l, r].


class PrefixSumsMod:
    __slots__ = ("n", "P", "mod")

    # O(N) -- arr: the array (a list, can be empty)
    def __init__(self, arr, mod=10**9 + 7):
        self.mod = mod
        self.n = len(arr)
        P = self.P = [0] * (self.n + 1)
        for i, v in enumerate(arr):
            P[i + 1] = (P[i] + v) % mod

    # O(1) -- (a[l] + ... + a[r]) % MOD, in [0, mod); needs 0 <= l <= r < n, else IndexError
    def rangeSumMod(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSumMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return (self.P[r + 1] - self.P[l]) % self.mod
