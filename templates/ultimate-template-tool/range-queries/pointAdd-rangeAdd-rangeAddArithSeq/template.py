# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-rangeAdd-rangeAddArithSeq/template.py
# @operations: getAll pointAdd rangeAdd rangeAddArithSeq
# @data-structure-type: difference-array
# @complexities:
#   getAll: N
#   pointAdd: 1
#   rangeAdd: 1
#   rangeAddArithSeq: 1
#   build: N
# @memory:
#   layout: none
#   node: dk[1*N] ds[1*N]
#   tags: none
#   other: a[1*N]
#   note: every add is a line k + s * i over [l, r]; dk and ds are difference arrays of k and s, and getAll sweeps both

# Range add and arithmetic sequence add, then read the array: two difference arrays (a double sweep line). An add of
# start, start + step, ... over [l, r] is the line k + step * i with k = start - l * step, so it is O(1): k and step go
# into one difference array each, and getAll sweeps both and adds k + step * i at every i, O(N). getAll can be called
# again later (the adds are kept). Nothing reads a single value in between: for that, use a BIT or seg tree. All
# indices 0-based, ranges inclusive [l, r].


class DiffArrayArith:
    __slots__ = ("n", "a", "dk", "ds")

    # O(N) -- arr: the initial array (a list, can be empty)
    def __init__(self, arr):
        self.n = len(arr)
        self.a = list(arr)
        self.dk = [0] * (self.n + 1)
        self.ds = [0] * (self.n + 1)

    # O(1) -- a[l + j] += start + j * step for j in [0, r - l]; needs 0 <= l <= r < n, else IndexError
    def rangeAddArithSeq(self, l, r, start, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAddArithSeq: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        k = start - l * step
        self.dk[l] += k
        self.dk[r + 1] -= k
        self.ds[l] += step
        self.ds[r + 1] -= step

    # O(1) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self.dk[l] += v
        self.dk[r + 1] -= v

    # O(1) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.dk[i] += v
        self.dk[i + 1] -= v

    # O(N) -- the whole array with every add so far applied (a new list)
    def getAll(self):
        out, k, s, dk, ds = list(self.a), 0, 0, self.dk, self.ds
        for i in range(self.n):
            k += dk[i]
            s += ds[i]
            out[i] += k + s * i
        return out
