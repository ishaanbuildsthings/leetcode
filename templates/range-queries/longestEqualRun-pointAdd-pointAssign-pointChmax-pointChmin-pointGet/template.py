# @operations: longestEqualRun pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: seg-tree
# @complexities:
#   longestEqualRun: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: ln[2*N] pre[2*N] suf[2*N] best[2*N] lv[2*N] rv[2*N]
#   tags: none
#   other: none
#   note: per node: length, equal-run at the left / right end, best run inside, and the end values; queries fold a left and a right accumulator
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/LongestContiguousBlockSeg.cpp

# Longest run of equal adjacent values inside a[l..r], with point updates. All indices 0-based, ranges inclusive.
# Iterative 2N tree. Merging A then B: the runs at the seam join when A's last value == B's first value. The merge
# is not commutative, so a query folds a left accumulator and a right accumulator, then joins them.


class EqualRunTree:
    __slots__ = ("n", "ln", "pre", "suf", "best", "lv", "rv")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.ln = [0] * n + [1] * n
        self.pre = [0] * n + [1] * n
        self.suf = [0] * n + [1] * n
        self.best = [0] * n + [1] * n
        self.lv = [0] * n + list(arr)
        self.rv = [0] * n + list(arr)
        for x in range(n - 1, 0, -1):
            self._pull(x)

    @staticmethod
    def _merge(a, b):
        aln, apre, asuf, abest, alv, arv = a
        bln, bpre, bsuf, bbest, blv, brv = b
        join = arv == blv
        pre = apre + bpre if join and apre == aln else apre
        suf = bsuf + asuf if join and bsuf == bln else bsuf
        best = abest if abest > bbest else bbest
        if join and asuf + bpre > best:
            best = asuf + bpre
        return aln + bln, pre, suf, best, alv, brv

    def _node(self, x):
        return self.ln[x], self.pre[x], self.suf[x], self.best[x], self.lv[x], self.rv[x]

    def _pull(self, x):
        self.ln[x], self.pre[x], self.suf[x], self.best[x], self.lv[x], self.rv[x] = self._merge(self._node(2 * x), self._node(2 * x + 1))

    # O(logN) -- length of the longest block of equal adjacent values inside a[l..r]
    def longestEqualRun(self, l, r):
        left = right = None
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                left = self._node(l) if left is None else self._merge(left, self._node(l))
                l += 1
            if r & 1:
                r -= 1
                right = self._node(r) if right is None else self._merge(self._node(r), right)
            l >>= 1
            r >>= 1
        if left is None:
            return right[3]
        if right is None:
            return left[3]
        return self._merge(left, right)[3]

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        p = i + self.n
        self.lv[p] = self.rv[p] = val
        p >>= 1
        while p:
            self._pull(p)
            p >>= 1

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.lv[i + self.n]

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.lv[i + self.n] + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.lv[i + self.n]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.lv[i + self.n]:
            self.pointAssign(i, val)
