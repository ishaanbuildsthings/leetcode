# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostPrefixSumGtX-leftmostPrefixSumGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/template.py
# @operations: leftmostPrefixSumGtX leftmostPrefixSumGteX pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
# @data-structure-type: BIT
# @complexities:
#   leftmostPrefixSumGtX: log(N)
#   leftmostPrefixSumGteX: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: none
#   node: tree[1*N]
#   tags: none
#   other: none
#   note: the prefix-sum searches binary-lift over the tree, so they need every a[i] >= 0
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/pointAddRangeSumBIT.py

# used in https://leetcode.com/problems/sum-of-beautiful-subsequences/submissions/1973972991/
class BIT:
    __slots__ = ['n', 'tree']
    def __init__(self, arr):
        self.n = len(arr)
        n = self.n
        tree = self.tree = [0] + list(arr)
        # O(N) -- push each node into its parent once
        for i in range(1, n + 1):
            j = i + (i & -i)
            if j <= n:
                tree[j] += tree[i]

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        i += 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)

    # gets prefix sum 0...i
    def queryPf(self, i):
        s = 0
        i += 1
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)
        return s

    # gets sum l...r
    def rangeSum(self, l, r):
        if l > r:
            return 0
        if l == 0:
            return self.queryPf(r)
        return self.queryPf(r) - self.queryPf(l - 1)

    # O(logN) -- a[i] in one walk instead of two prefix sums
    def pointGet(self, i):
        tree = self.tree
        i += 1
        val = tree[i]
        stop = i - (i & -i)
        i -= 1
        while i > stop:
            val -= tree[i]
            i -= i & -i
        return val

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        self.pointAdd(i, val - self.pointGet(i))

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.pointAdd(i, val - cur)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.pointAdd(i, val - cur)
    # O(logN) -- smallest i with a[0] + ... + a[i] >= target (> target if strict), or n if none.
    # Binary lifting: grow pos by powers of two while the prefix stays below target. Needs every a[i] >= 0.
    def _prefixLowerBound(self, target, strict):
        tree, n = self.tree, self.n
        pos = acc = 0
        step = 1 << (n.bit_length() - 1) if n else 0
        while step:
            nxt = pos + step
            if nxt <= n:
                v = acc + tree[nxt]
                if v < target or (strict and v == target):
                    pos, acc = nxt, v
            step >>= 1
        return pos

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1. Needs every a[i] >= 0.
    # e.g. on a 0/1 array, leftmostPrefixSumGteX(0, n - 1, k) is the index of the k-th one.
    def leftmostPrefixSumGteX(self, l, r, x):
        i = self._prefixLowerBound(self.queryPf(l - 1) + x, False)
        if i < l:
            i = l
        return i if i <= r else -1

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] > x, or -1. Needs every a[i] >= 0.
    def leftmostPrefixSumGtX(self, l, r, x):
        i = self._prefixLowerBound(self.queryPf(l - 1) + x, True)
        if i < l:
            i = l
        return i if i <= r else -1
