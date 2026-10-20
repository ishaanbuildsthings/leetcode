# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/costMonoIncreasing-pointGet-rangeSum/template.py
# @operations: costMonoIncreasing pointGet rangeSum
# @data-structure-type: sparse-table
# @complexities:
#   costMonoIncreasing: 1
#   pointGet: 1
#   rangeSum: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: sp[1*N*log(N)]
#   tags: none
#   other: arr[1*N] pf[1*N] suff[1*N]
#   note: sp is a sparse table of argmax indices; arr is a private copy of the input
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/costToMakeSubarrayMonoIncreasing.py

from itertools import accumulate

# compute the cost to make an array from l...r mono-increasing where a single cost lets us increment an index by 1
# O(n log n) build, O(1) query range
class MonoIncreaseCost:
    """Min increments to make a range non-decreasing (increments only).
    Build: O(n log n) time and space.  query: O(1).  Static array."""

    def __init__(self, arr):
        self.arr = list(arr)
        n = self.n = len(arr)
        self.pf = list(accumulate(arr, initial=0))

        # suff[i] = sum of prefix maxes over [i, n-1], measured from i
        suff = [0] * (n + 1)
        st = []
        for i in range(n - 1, -1, -1):
            while st and arr[st[-1]] <= arr[i]:
                st.pop()
            nxt = st[-1] if st else n
            suff[i] = arr[i] * (nxt - i) + suff[nxt]
            st.append(i)
        self.suff = suff

        # sparse table of argmax
        self.sp = [list(range(n))]
        j = 1
        while (1 << j) <= n:
            prev = self.sp[-1]
            half = 1 << (j - 1)
            cur = [0] * (n - (1 << j) + 1)
            for i in range(len(cur)):
                a, b = prev[i], prev[i + half]
                cur[i] = a if arr[a] >= arr[b] else b
            self.sp.append(cur)
            j += 1

    # O(1) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self.pf[r + 1] - self.pf[l] if r >= l else 0

    def argMax(self, l, r):
        j = (r - l + 1).bit_length() - 1
        a = self.sp[j][l]
        b = self.sp[j][r - (1 << j) + 1]
        return a if self.arr[a] >= self.arr[b] else b

    # O(1) -- min +1 increments to make a[l..r] non-decreasing
    def costMonoIncreasing(self, l, r):
        """Min increments to make arr[l..r] non-decreasing. O(1)."""
        m = self.argMax(l, r)
        endsAt = (self.suff[l] - self.suff[m]) + self.arr[m] * (r - m + 1)
        return endsAt - self.rangeSum(l, r)

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]