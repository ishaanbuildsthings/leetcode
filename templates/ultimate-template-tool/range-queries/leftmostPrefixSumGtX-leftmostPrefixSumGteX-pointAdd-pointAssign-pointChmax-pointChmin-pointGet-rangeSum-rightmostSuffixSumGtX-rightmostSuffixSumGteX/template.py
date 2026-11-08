# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostPrefixSumGtX-leftmostPrefixSumGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum-rightmostSuffixSumGtX-rightmostSuffixSumGteX/template.py
# @operations: getAll leftmostPrefixSumGtX leftmostPrefixSumGteX pointAdd pointAssign pointChmax pointChmin pointGet rangeSum rightmostSuffixSumGtX rightmostSuffixSumGteX sumAll
# @data-structure-type: BIT
# @complexities:
#   getAll: N
#   leftmostPrefixSumGtX: log(N)
#   leftmostPrefixSumGteX: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeSum: log(N)
#   rightmostSuffixSumGtX: log(N)
#   rightmostSuffixSumGteX: log(N)
#   sumAll: log(N)
#   build: N
# @memory:
#   layout: none
#   node: tree[1*N]
#   tags: none
#   other: none
#   note: the prefix / suffix-sum searches binary-lift over the tree, so they need every a[i] >= 0
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

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
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

    # gets sum l...r; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return 0
        if l == 0:
            return self.queryPf(r)
        return self.queryPf(r) - self.queryPf(l - 1)

    # O(logN) -- a[i] in one walk instead of two prefix sums; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        tree = self.tree
        i += 1
        val = tree[i]
        stop = i - (i & -i)
        i -= 1
        while i > stop:
            val -= tree[i]
            i -= i & -i
        return val

    # O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    # i + lowbit(i) once complete)
    def getAll(self):
        n = self.n
        t = self.tree[:]
        for i in range(n, 0, -1):
            j = i + (i & -i)
            if j <= n:
                t[j] -= t[i]
        return t[1:]

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAdd(i, val - self.pointGet(i))

    # O(logN) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        cur = self.pointGet(i)
        if val > cur:
            self.pointAdd(i, val - cur)

    # O(logN) -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
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

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1. Needs every a[i] >= 0. e.g. on a 0/1 array,
    # leftmostPrefixSumGteX(0, n - 1, k) is the index of the k-th one.; needs 0 <= l <= r < n, else IndexError
    def leftmostPrefixSumGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostPrefixSumGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        i = self._prefixLowerBound(self.queryPf(l - 1) + x, False)
        if i < l:
            i = l
        return i if i <= r else -1

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] > x, or -1. Needs every a[i] >= 0.; needs 0 <= l <= r < n,
    # else IndexError
    def leftmostPrefixSumGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostPrefixSumGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        i = self._prefixLowerBound(self.queryPf(l - 1) + x, True)
        if i < l:
            i = l
        return i if i <= r else -1

    # O(logN) -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1. Needs every a[i] >= 0. That is the last i with
    # a[0] + ... + a[i - 1] <= prefix(r) - x: one binary lift.; needs 0 <= l <= r < n, else IndexError
    def rightmostSuffixSumGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostSuffixSumGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        t = self.queryPf(r) - x
        if t < 0:
            return -1
        i = min(r, self._prefixLowerBound(t, True))
        return i if i >= l else -1

    # O(logN) -- last i in [l, r] with a[i] + ... + a[r] > x, or -1. Needs every a[i] >= 0.; needs
    # 0 <= l <= r < n, else IndexError
    def rightmostSuffixSumGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostSuffixSumGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        t = self.queryPf(r) - x
        if t <= 0:
            return -1
        i = min(r, self._prefixLowerBound(t, False))
        return i if i >= l else -1

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)
