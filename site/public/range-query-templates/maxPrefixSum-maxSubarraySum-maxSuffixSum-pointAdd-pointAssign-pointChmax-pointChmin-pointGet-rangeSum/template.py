# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxPrefixSum-maxSubarraySum-maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/template.py
# @operations: getAll maxPrefixSum maxSubarraySum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum sumAll
# @data-structure-type: seg-tree
# @letters: same
# @complexities:
#   getAll: N
#   maxPrefixSum: log(N)
#   maxSubarraySum: log(N)
#   maxSuffixSum: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   rangeSum: log(N)
#   sumAll: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] pre[2*N] suf[2*N] best[2*N]
#   tags: none
#   other: none
#   note: each node is (sum, best prefix, best suffix, best subarray); the merge is not commutative, so a query folds a left and a right accumulator

# Max subarray / max prefix / max suffix sum of a range, plus range sum, with point updates.
# All indices 0-based, ranges inclusive [l, r]. All three maxima are over NON-EMPTY pieces; when the empty piece is
# allowed (answer >= 0), take max(0, ...).
# Iterative 2N tree. Merging (sum, pre, suf, best) is not commutative, so a query folds nodes into a left accumulator
# (left to right) and a right accumulator (right to left), then joins the two.


class MaxSubarrayTree:
    __slots__ = ("n", "sm", "pre", "suf", "best")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.sm = [0] * n + list(arr)
        self.pre = [0] * n + list(arr)
        self.suf = [0] * n + list(arr)
        self.best = [0] * n + list(arr)
        for x in range(n - 1, 0, -1):
            self._pull(x)

    def _pull(self, x):
        sm, pre, suf, best = self.sm, self.pre, self.suf, self.best
        a, b = 2 * x, 2 * x + 1
        sm[x] = sm[a] + sm[b]
        pre[x] = max(pre[a], sm[a] + pre[b])
        suf[x] = max(suf[b], sm[b] + suf[a])
        best[x] = max(best[a], best[b], suf[a] + pre[b])

    # O(logN) -- (sum, best prefix, best suffix, best subarray) of a[l..r], l <= r
    def _query(self, l, r):
        sm, pre, suf, best = self.sm, self.pre, self.suf, self.best
        ls = lp = lu = lb = 0  # left accumulator: everything folded so far from the left
        rs = rp = ru = rb = 0  # right accumulator: everything folded so far from the right
        lEmpty = rEmpty = True
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                if lEmpty:
                    ls, lp, lu, lb, lEmpty = sm[l], pre[l], suf[l], best[l], False
                else:  # (acc) + (node l)
                    lb = max(lb, best[l], lu + pre[l])
                    lp = max(lp, ls + pre[l])
                    lu = max(suf[l], sm[l] + lu)
                    ls += sm[l]
                l += 1
            if r & 1:
                r -= 1
                if rEmpty:
                    rs, rp, ru, rb, rEmpty = sm[r], pre[r], suf[r], best[r], False
                else:  # (node r) + (acc)
                    rb = max(rb, best[r], suf[r] + rp)
                    rp = max(pre[r], sm[r] + rp)
                    ru = max(ru, rs + suf[r])
                    rs += sm[r]
            l >>= 1
            r >>= 1
        if rEmpty:
            return ls, lp, lu, lb
        if lEmpty:
            return rs, rp, ru, rb
        return ls + rs, max(lp, ls + rp), max(ru, rs + lu), max(lb, rb, lu + rp)

    # O(logN) -- max over l <= i <= j <= r of a[i] + ... + a[j]; needs 0 <= l <= r < n, else IndexError
    def maxSubarraySum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxSubarraySum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._query(l, r)[3]

    # O(logN) -- max over l <= i <= r of a[l] + ... + a[i]; needs 0 <= l <= r < n, else IndexError
    def maxPrefixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxPrefixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._query(l, r)[1]

    # O(logN) -- max over l <= i <= r of a[i] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def maxSuffixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxSuffixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._query(l, r)[2]

    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._query(l, r)[0] if l <= r else 0

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self.sm[p] = self.pre[p] = self.suf[p] = self.best[p] = val
        p >>= 1
        while p:
            self._pull(p)
            p >>= 1

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.sm[i + self.n]

    # O(N) -- the whole array (a copy of the leaves)
    def getAll(self):
        return self.sm[self.n:]

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.sm[i + self.n] + delta)

    # O(logN) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.sm[i + self.n]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val); needs needs 0 <= i < n, else IndexError, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.sm[i + self.n]:
            self.pointAssign(i, val)
