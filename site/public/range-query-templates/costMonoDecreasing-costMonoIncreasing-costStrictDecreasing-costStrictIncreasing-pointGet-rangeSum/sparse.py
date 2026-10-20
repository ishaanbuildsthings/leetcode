# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/costMonoDecreasing-costMonoIncreasing-costStrictDecreasing-costStrictIncreasing-pointGet-rangeSum/sparse.py
# @operations: costMonoDecreasing costMonoIncreasing costStrictDecreasing costStrictIncreasing pointGet rangeSum
# @data-structure-type: sparse-table
# @complexities:
#   costMonoDecreasing: log(N)
#   costMonoIncreasing: log(N)
#   costStrictDecreasing: log(N)
#   costStrictIncreasing: log(N)
#   pointGet: log(N)
#   rangeSum: log(N)
#   build: N*log(N)
# @memory:
#   layout: sparse
#   node: sp[8*N*log(N)]
#   tags: none
#   other: idx[1*N] vals[1*N] starts[8*N] v[8*N] w[8*N] W[8*N] B[8*N] suff[8*N]
#   note: built from N (index, value) points over any index range [lo, hi], every other index 0; a view is the array cut into pieces (each point, each gap of zeros), with a sparse table of argmax and next-greater sums over the pieces; four views: a, a mirrored, a[i] - i, and a mirrored minus its index (decreasing costs are increasing costs on the mirror, strict costs subtract the index); each view is built on its first query
from bisect import bisect_left, bisect_right


class _PieceCost:
    """costMonoIncreasing (min +1 increments to make a[l..r] non-decreasing) over an array given as pieces: piece k
    starts at index starts[k], spans w[k] indices, and holds v[k] + slope[k] * t at its t-th index (slope 0 or -1,
    so a piece's own max is its first value). cost = sum of prefix maxes - sum of values. The prefix max is flat
    inside a piece, so sum over pieces of w * max(carry, max of v so far): a sparse table of argmax finds the first
    piece above the carry and the max, and suff[k] = sum over j >= k of w_j * max(v[k..j]) (by next-greater) does the
    rest."""
    __slots__ = ("starts", "v", "w", "slope", "W", "B", "sp", "suff")

    # O(N log N)
    def __init__(self, starts, v, w, slope):
        n = len(v)
        self.starts, self.v, self.w, self.slope = starts, v, w, slope
        W, B = [0] * (n + 1), [0] * (n + 1)  # prefix weights, prefix value sums
        for k in range(n):
            W[k + 1] = W[k] + w[k]
            B[k + 1] = B[k] + w[k] * v[k] + slope[k] * w[k] * (w[k] - 1) // 2
        self.W, self.B = W, B
        sp = [list(range(n))]  # sp[j][k] = index of the (leftmost) max of v[k .. k + 2^j - 1]
        j = 1
        while (1 << j) <= n:
            prev, h = sp[-1], 1 << (j - 1)
            sp.append([prev[k] if v[prev[k]] >= v[prev[k + h]] else prev[k + h] for k in range(n - (1 << j) + 1)])
            j += 1
        self.sp = sp
        suff, stack = [0] * (n + 1), []
        for k in range(n - 1, -1, -1):
            while stack and v[stack[-1]] <= v[k]:
                stack.pop()
            ng = stack[-1] if stack else n
            suff[k] = v[k] * (W[ng] - W[k]) + suff[ng]
            stack.append(k)
        self.suff = suff

    def _argmax(self, a, b):
        j = (b - a + 1).bit_length() - 1
        x, y = self.sp[j][a], self.sp[j][b - (1 << j) + 1]
        return x if self.v[x] >= self.v[y] else y

    def _carry(self, a, b, M):  # sum over pieces k in [a, b] of w_k * max(M, max(v[a..k]))
        v, W, sp = self.v, self.W, self.sp
        q = a  # first piece in [a, b] above M: skip blocks whose max is <= M
        for j in range(len(sp) - 1, -1, -1):
            if q + (1 << j) - 1 <= b and v[sp[j][q]] <= M:
                q += 1 << j
        if q > b:
            return M * (W[b + 1] - W[a])
        p = self._argmax(q, b)
        return M * (W[q] - W[a]) + self.suff[q] - self.suff[p] + v[p] * (W[b + 1] - W[p])

    def _part(self, k, x, y):  # sum of piece k's values at indices x..y
        n = y - x + 1
        return n * (self.v[k] + self.slope[k] * (x - self.starts[k])) + self.slope[k] * n * (n - 1) // 2

    # O(logN) -- a[l] + ... + a[r]
    def sum(self, l, r):
        starts, w = self.starts, self.w
        k0, k1 = bisect_right(starts, l) - 1, bisect_right(starts, r) - 1
        if k0 == k1:
            return self._part(k0, l, r)
        return self._part(k0, l, starts[k0] + w[k0] - 1) + self.B[k1] - self.B[k0 + 1] + self._part(k1, starts[k1], r)

    # O(logN) -- min +1 increments to make a[l..r] non-decreasing
    def cost(self, l, r):
        starts, v, w = self.starts, self.v, self.w
        k0, k1 = bisect_right(starts, l) - 1, bisect_right(starts, r) - 1
        m0 = v[k0] + self.slope[k0] * (l - starts[k0])  # the value at l: the prefix max all through l's piece
        if k0 == k1:
            return (r - l + 1) * m0 - self.sum(l, r)
        pref = m0 * (starts[k0] + w[k0] - l) + self._carry(k0 + 1, k1, m0)
        final = max(m0, v[self._argmax(k0 + 1, k1)])  # the prefix max all through r's piece
        pref -= (starts[k1] + w[k1] - 1 - r) * final  # r's piece only counts up to r
        return pref - self.sum(l, r)


def _pieces(lo, hi, pts, c):
    """The pieces of b[i] = a[i] + c * (i - lo) (c = 0, or -1 for the strict costs) for points pts over [lo, hi]."""
    starts, v, w, slope = [], [], [], []
    prev = lo - 1
    for i, x in pts:
        if i > prev + 1:
            starts.append(prev + 1), v.append(c * (prev + 1 - lo)), w.append(i - prev - 1), slope.append(c)
        starts.append(i), v.append(x + c * (i - lo)), w.append(1), slope.append(0)
        prev = i
    if prev < hi:
        starts.append(prev + 1), v.append(c * (prev + 1 - lo)), w.append(hi - prev), slope.append(c)
    return starts, v, w, slope


# Min +1 increments to make a[l..r] non-decreasing / non-increasing / strictly increasing / strictly decreasing,
# and range sum, over any index range [lo, hi], built from (index, value) points; every other index is 0.
# Decreasing costs are increasing costs on the mirror image (index i -> lo + hi - i); strict costs are the
# non-strict ones on a[i] - i (shifting by a constant changes nothing). Each view is built on its first query.


class SparseMonoCosts:
    __slots__ = ("lo", "hi", "idx", "vals", "pts", "views")

    # O(N log N) -- [lo, hi] all 0 except the given (index, value) points (distinct indices)
    def __init__(self, lo, hi, points):
        self.lo, self.hi = lo, hi
        self.pts = sorted(points)
        self.idx = [i for i, _ in self.pts]
        self.vals = [v for _, v in self.pts]
        self.views = {}

    def _view(self, mirrored, c):
        key = (mirrored, c)
        if key not in self.views:
            lo, hi = self.lo, self.hi
            pts = sorted((lo + hi - i, x) for i, x in self.pts) if mirrored else self.pts
            self.views[key] = _PieceCost(*_pieces(lo, hi, pts, c))
        return self.views[key]

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._view(False, 0).sum(l, r) if l <= r else 0

    # O(logN) -- min +1 increments to make a[l..r] non-decreasing
    def costMonoIncreasing(self, l, r):
        return self._view(False, 0).cost(l, r)

    # O(logN) -- min +1 increments to make a[l..r] non-increasing
    def costMonoDecreasing(self, l, r):
        return self._view(True, 0).cost(self.lo + self.hi - r, self.lo + self.hi - l)

    # O(logN) -- min +1 increments to make a[l..r] strictly increasing
    def costStrictIncreasing(self, l, r):
        return self._view(False, -1).cost(l, r)

    # O(logN) -- min +1 increments to make a[l..r] strictly decreasing
    def costStrictDecreasing(self, l, r):
        return self._view(True, -1).cost(self.lo + self.hi - r, self.lo + self.hi - l)

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
