# @operations: maxPrefixSum maxSubarraySum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
# @data-structure-type: seg-tree
# @complexities:
#   maxPrefixSum: log(N)
#   maxSubarraySum: log(N)
#   maxSuffixSum: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   rangeSum: log(N)
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

    # O(logN) -- max over l <= i <= j <= r of a[i] + ... + a[j]
    def maxSubarraySum(self, l, r):
        return self._query(l, r)[3]

    # O(logN) -- max over l <= i <= r of a[l] + ... + a[i]
    def maxPrefixSum(self, l, r):
        return self._query(l, r)[1]

    # O(logN) -- max over l <= i <= r of a[i] + ... + a[r]
    def maxSuffixSum(self, l, r):
        return self._query(l, r)[2]

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._query(l, r)[0] if l <= r else 0

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        p = i + self.n
        self.sm[p] = self.pre[p] = self.suf[p] = self.best[p] = val
        p >>= 1
        while p:
            self._pull(p)
            p >>= 1

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.sm[i + self.n]

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.sm[i + self.n] + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.sm[i + self.n]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.sm[i + self.n]:
            self.pointAssign(i, val)
