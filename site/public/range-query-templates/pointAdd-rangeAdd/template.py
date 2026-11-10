# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-rangeAdd/template.py
# @operations: getAll pointAdd rangeAdd
# @data-structure-type: difference-array
# @complexities:
#   getAll: N
#   pointAdd: 1
#   rangeAdd: 1
#   build: N
# @memory:
#   layout: none
#   node: d[1*N]
#   tags: none
#   other: a[1*N]
#   note: d is the difference array of every add so far (d[l] += v, d[r+1] -= v); getAll sweeps it once

# Range add, then read the array: a difference array (a sweep line). Every add is O(1); getAll is one O(N) prefix sum
# pass over the adds, and it can be called again later (the adds are kept). Nothing reads a single value in between:
# for that, use a BIT or seg tree. All indices 0-based, ranges inclusive [l, r].


class DiffArray:
    __slots__ = ("n", "a", "d")

    # O(N) -- arr: the initial array (a list, can be empty)
    def __init__(self, arr):
        self.n = len(arr)
        self.a = list(arr)
        self.d = [0] * (self.n + 1)

    # O(1) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self.d[l] += v
        self.d[r + 1] -= v

    # O(1) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.d[i] += v
        self.d[i + 1] -= v

    # O(N) -- the whole array with every add so far applied (a new list)
    def getAll(self):
        out, run, d = list(self.a), 0, self.d
        for i in range(self.n):
            run += d[i]
            out[i] += run
        return out
