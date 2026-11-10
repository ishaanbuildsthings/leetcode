# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-rangeAddMod/template.py
# @operations: getAll pointAdd rangeAddMod
# @data-structure-type: difference-array
# @complexities:
#   getAll: N
#   pointAdd: 1
#   rangeAddMod: 1
#   build: N
# @memory:
#   layout: none
#   node: d[1*N]
#   tags: none
#   other: a[1*N]
#   note: d is the difference array of every add so far, % MOD (d[l] += v, d[r+1] -= v); getAll sweeps it once

# Range add % MOD, then read the array: a difference array (a sweep line). Every add is O(1); getAll is one O(N) prefix
# sum pass over the adds, and it can be called again later (the adds are kept). Nothing reads a single value in
# between: for that, use a BIT or seg tree. Values are kept in [0, mod). All indices 0-based, ranges inclusive [l, r].


class DiffArrayMod:
    __slots__ = ("n", "a", "d", "mod")

    # O(N) -- arr: the initial array (a list, can be empty)
    def __init__(self, arr, mod=10**9 + 7):
        self.mod = mod
        self.n = len(arr)
        self.a = [v % mod for v in arr]
        self.d = [0] * (self.n + 1)

    # O(1) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAddMod(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAddMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        d, mod = self.d, self.mod
        d[l] = (d[l] + v) % mod
        d[r + 1] = (d[r + 1] - v) % mod

    # O(1) -- a[i] += v (% MOD); needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAddMod(i, i, v)

    # O(N) -- the whole array with every add so far applied, each value in [0, mod) (a new list)
    def getAll(self):
        out, run, d, mod = list(self.a), 0, self.d, self.mod
        for i in range(self.n):
            run = (run + d[i]) % mod
            out[i] = (out[i] + run) % mod
        return out
