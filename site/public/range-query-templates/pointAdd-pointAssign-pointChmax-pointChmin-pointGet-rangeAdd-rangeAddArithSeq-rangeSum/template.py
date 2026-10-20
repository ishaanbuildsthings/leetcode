# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAddArithSeq-rangeSum/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAddArithSeq rangeSum
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeAddArithSeq: log(N)
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: none
#   node: bA[1*N] bB[1*N] bC[1*N]
#   tags: none
#   other: none
#   note: prefix sums are kept as A(x) + B(x) * x + C(x) * x(x+1)/2 with A, B, C three Fenwick trees

# Range add of an arithmetic sequence (and plain range add) + range sum with three Fenwick trees, no lazy tags.
# All indices 0-based, ranges inclusive [l, r].
# Adding c0 + c1 * i to every i in [l, r] changes the prefix sum P(x) = a[0] + ... + a[x] by
#   x in [l, r]:  c0 * (x - l + 1) + c1 * (T(x) - T(l - 1))        T(k) = k * (k + 1) / 2
#   x > r:        the whole added total
# so keep P(x) = A(x) + B(x) * x + C(x) * T(x), where A, B, C are prefix sums of point updates made at l and r + 1.
# Using T(x) instead of x^2 keeps every coefficient an integer (no division by 2).


def _tri(k):
    return k * (k + 1) // 2


class ArithSeqSumBIT:
    __slots__ = ("n", "bA", "bB", "bC")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        bA = self.bA = [0] * (n + 1)
        self.bB = [0] * (n + 1)
        self.bC = [0] * (n + 1)
        for i, v in enumerate(arr):  # a[i] alone adds v to every P(x) with x >= i
            bA[i + 1] = v
        for i in range(1, n + 1):
            j = i + (i & -i)
            if j <= n:
                bA[j] += bA[i]

    def _point(self, i, a, b, c):
        bA, bB, bC, n = self.bA, self.bB, self.bC, self.n
        i += 1
        while i <= n:
            bA[i] += a
            bB[i] += b
            bC[i] += c
            i += i & -i

    # O(logN) -- a[0] + ... + a[x] (0 for x = -1)
    def _prefix(self, x):
        bA, bB, bC = self.bA, self.bB, self.bC
        sa = sb = sc = 0
        i = x + 1
        while i > 0:
            sa += bA[i]
            sb += bB[i]
            sc += bC[i]
            i &= i - 1
        return sa + sb * x + sc * _tri(x)

    # O(logN) -- a[l + j] += start + j * step for j in [0, r - l]
    def rangeAddArithSeq(self, l, r, start, step):
        if l > r:
            return
        c0, c1 = start - step * l, step  # adding c0 + c1 * i at index i
        a = c0 * (1 - l) - c1 * _tri(l - 1)
        self._point(l, a, c0, c1)
        if r + 1 < self.n:
            total = c0 * (r - l + 1) + c1 * (_tri(r) - _tri(l - 1))
            self._point(r + 1, total - a, -c0, -c1)

    # O(logN) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        self.rangeAddArithSeq(l, r, v, 0)

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._prefix(r) - self._prefix(l - 1) if l <= r else 0

    # O(logN) -- a[i]
    def pointGet(self, i):
        return self.rangeSum(i, i)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAdd(i, i, delta)

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAdd(i, i, val - self.pointGet(i))

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.rangeAdd(i, i, val - cur)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.rangeAdd(i, i, val - cur)
