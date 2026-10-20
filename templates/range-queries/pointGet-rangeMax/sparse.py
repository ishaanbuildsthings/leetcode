# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeMax/sparse.py
# @operations: pointGet rangeMax
# @data-structure-type: sparse-table
# @complexities:
#   pointGet: log(N)
#   rangeMax: log(N)
#   build: N*log(N)
# @memory:
#   layout: sparse
#   node: sparse[2*N*log(N)]
#   tags: none
#   other: idx[1*N] vals[1*N] starts[2*N]
#   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; the sparse table runs on the given values plus one 0 per gap (at most 2N + 1 elements)
# MAX sparse table
# O(n log n) build
# O(1) range MAX

class SparseMax:
    def __init__(self, arr):
        self.n = len(arr)
        self.LOG = self.n.bit_length()
        self.sparse = [[0] * self.n for _ in range(self.LOG)]
        for i in range(self.n):
            self.sparse[0][i] = arr[i]
        for power in range(1, self.LOG):
            halfWidth = 1 << (power - 1)
            for left in range(self.n):
                val = self.sparse[power - 1][left]
                rightEdge = left + halfWidth
                if rightEdge < self.n:
                    val = max(val, self.sparse[power - 1][rightEdge])
                self.sparse[power][left] = val

    # O(1) -- max of a[l..r]
    def rangeMax(self, l, r):
        width = r - l + 1
        maxPow = width.bit_length() - 1
        powWidth = 1 << maxPow
        return max(
            self.sparse[maxPow][l],
            self.sparse[maxPow][l + width - powWidth]
        )

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.sparse[0][i]

# ======================================================================================== sparse wrapper

from bisect import bisect_left, bisect_right


# Range max over any index range [lo, hi], built from given values (index, value pairs); every other index is 0. A maximal gap
# of zeros adds nothing more than a single 0, so SparseMax runs on the compressed array of given values with one 0 per gap,
# and a query maps l and r to the compressed elements containing them.


class SparseStaticMax:
    __slots__ = ("lo", "hi", "idx", "vals", "starts", "inner")

    # O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    def __init__(self, lo, hi, values):
        self.lo, self.hi = lo, hi
        pts = sorted(values)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        starts, arr = [], []  # starts[k] = first index of compressed element k
        prev = lo - 1
        for i, v in pts:
            if i > prev + 1:
                starts.append(prev + 1)
                arr.append(0)
            starts.append(i)
            arr.append(v)
            prev = i
        if prev < hi:
            starts.append(prev + 1)
            arr.append(0)
        self.starts = starts
        self.inner = SparseMax(arr)

    # O(logN) -- range max of a[l..r]
    def rangeMax(self, l, r):
        return self.inner.rangeMax(bisect_right(self.starts, l) - 1, bisect_right(self.starts, r) - 1)

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
