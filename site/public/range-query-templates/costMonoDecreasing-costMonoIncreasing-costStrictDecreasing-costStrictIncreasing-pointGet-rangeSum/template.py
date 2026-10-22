# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/costMonoDecreasing-costMonoIncreasing-costStrictDecreasing-costStrictIncreasing-pointGet-rangeSum/template.py
# @operations: costMonoDecreasing costMonoIncreasing costStrictDecreasing costStrictIncreasing pointGet rangeSum
# @data-structure-type: sparse-table
# @complexities:
#   costMonoDecreasing: 1
#   costMonoIncreasing: 1
#   costStrictDecreasing: 1
#   costStrictIncreasing: 1
#   pointGet: 1
#   rangeSum: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: sp[1*N*log(N)]
#   tags: none
#   other: arr[2*N] pf[2*N] suff[1*N]
#   note: per cost kind you call (shown for one): each kind builds its own MonoIncreaseCost view (a, reversed a, a[i] - i, reversed a[i] + i) on its first query, so kinds you never call cost nothing; rangeSum / pointGet need no view
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/costToMakeSubarrayMonoIncreasing.py

from itertools import accumulate

# Min +1 increments to make a[l..r] non-decreasing / non-increasing / strictly increasing / strictly decreasing.
# Static array, all indices 0-based, ranges inclusive. Every query O(1) after an O(N log N) build per view.
# One structure answers "non-decreasing"; the other three reduce to it:
#   non-increasing on a        == non-decreasing on a reversed
#   strictly increasing on a   == non-decreasing on b[i] = a[i] - i      (a[i] < a[i+1]  <=>  b[i] <= b[i+1])
#   strictly decreasing on a   == non-increasing on c[i] = a[i] + i
# Adding the same +1 to a[i] adds it to b[i] / c[i], so the costs carry over unchanged.

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


class MonoCosts:
    __slots__ = ("n", "arr", "pf", "_inc", "_dec", "_sinc", "_sdec")

    # O(N); each cost kind builds its own O(N log N) view on its first query, so you only pay for the kinds you call
    def __init__(self, arr):
        self.n = len(arr)
        self.arr = list(arr)
        self.pf = list(accumulate(self.arr, initial=0))
        self._inc = self._dec = self._sinc = self._sdec = None

    # O(1) -- min +1 increments to make a[l..r] non-decreasing
    def costMonoIncreasing(self, l, r):
        if self._inc is None:
            self._inc = MonoIncreaseCost(self.arr)
        return self._inc.costMonoIncreasing(l, r)

    # O(1) -- min +1 increments to make a[l..r] non-increasing
    def costMonoDecreasing(self, l, r):
        if self._dec is None:
            self._dec = MonoIncreaseCost(self.arr[::-1])
        n = self.n
        return self._dec.costMonoIncreasing(n - 1 - r, n - 1 - l)

    # O(1) -- min +1 increments to make a[l..r] strictly increasing
    def costStrictIncreasing(self, l, r):
        if self._sinc is None:
            self._sinc = MonoIncreaseCost([v - i for i, v in enumerate(self.arr)])
        return self._sinc.costMonoIncreasing(l, r)

    # O(1) -- min +1 increments to make a[l..r] strictly decreasing
    def costStrictDecreasing(self, l, r):
        if self._sdec is None:
            n = self.n
            self._sdec = MonoIncreaseCost([self.arr[i] + i for i in range(n - 1, -1, -1)])
        n = self.n
        return self._sdec.costMonoIncreasing(n - 1 - r, n - 1 - l)

    # O(1) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self.pf[r + 1] - self.pf[l] if r >= l else 0

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]
