# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-rangeAddArithSeqMod-rangeAddMod/template.py
# @operations: getAll pointAdd rangeAddArithSeqMod rangeAddMod
# @data-structure-type: difference-array
# @complexities:
#   getAll: N
#   pointAdd: 1
#   rangeAddArithSeqMod: 1
#   rangeAddMod: 1
#   build: N
# @memory:
#   layout: none
#   node: dk[1*N] ds[1*N]
#   tags: none
#   other: a[1*N]
#   note: every add is a line k + s * i over [l, r], % MOD; dk and ds are difference arrays of k and s, and getAll sweeps both

# Range add and arithmetic sequence add % MOD, then read the array: two difference arrays (a double sweep line). An
# add of start, start + step, ... over [l, r] is the line k + step * i with k = start - l * step, so it is O(1): k and
# step go into one difference array each, and getAll sweeps both and adds k + step * i at every i, O(N). getAll can be
# called again later (the adds are kept). Nothing reads a single value in between: for that, use a BIT or seg tree.
# Values are kept in [0, mod). All indices 0-based, ranges inclusive [l, r].


class DiffArrayArithMod:
    __slots__ = ("n", "a", "dk", "ds", "mod")

    # O(N) -- arr: the initial array (a list, can be empty)
    def __init__(self, arr, mod=10**9 + 7):
        self.mod = mod
        self.n = len(arr)
        self.a = [v % mod for v in arr]
        self.dk = [0] * (self.n + 1)
        self.ds = [0] * (self.n + 1)

    # O(1) -- a[l + j] += start + j * step (% MOD) for j in [0, r - l]; needs 0 <= l <= r < n, else IndexError
    def rangeAddArithSeqMod(self, l, r, start, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAddArithSeqMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        dk, ds, mod = self.dk, self.ds, self.mod
        k = (start - l * step) % mod
        dk[l] = (dk[l] + k) % mod
        dk[r + 1] = (dk[r + 1] - k) % mod
        ds[l] = (ds[l] + step) % mod
        ds[r + 1] = (ds[r + 1] - step) % mod

    # O(1) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAddMod(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAddMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        dk, mod = self.dk, self.mod
        dk[l] = (dk[l] + v) % mod
        dk[r + 1] = (dk[r + 1] - v) % mod

    # O(1) -- a[i] += v (% MOD); needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAddMod(i, i, v)

    # O(N) -- the whole array with every add so far applied, each value in [0, mod) (a new list)
    def getAll(self):
        out, k, s, dk, ds, mod = list(self.a), 0, 0, self.dk, self.ds, self.mod
        for i in range(self.n):
            k = (k + dk[i]) % mod
            s = (s + ds[i]) % mod
            out[i] = (out[i] + k + s * i) % mod
        return out
