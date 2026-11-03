# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeXorApply/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeXorApply
# @data-structure-type: BIT
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeXorApply: log(N)
#   build: N
# @memory:
#   layout: none
#   node: tree[1*N]
#   tags: none
#   other: none
#   note: a Fenwick tree over the xor-difference array; a[i] is the prefix xor of differences up to i

# Range xor, point get. All indices 0-based, ranges inclusive [l, r].
class RangeXorBIT:
    __slots__ = ("n", "tree")

    # O(N) -- linear Fenwick build over a[i] ^ a[i - 1]
    def __init__(self, arr):
        n = self.n = len(arr)
        tree = self.tree = [0] * (n + 1)
        prev = 0
        for i in range(1, n + 1):
            v = arr[i - 1]
            tree[i] ^= v ^ prev
            prev = v
            j = i + (i & -i)
            if j <= n:
                tree[j] ^= tree[i]

    def _xor(self, i, x):
        tree, n = self.tree, self.n
        i += 1
        while i <= n:
            tree[i] ^= x
            i += i & -i

    # O(logN) -- a[i] for i in [l, r] ^= x; needs 0 <= l <= r < n, else IndexError
    def rangeXorApply(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeXorApply: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._xor(l, x)
        if r + 1 < self.n:
            self._xor(r + 1, x)

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        tree = self.tree
        s = 0
        i += 1
        while i:
            s ^= tree[i]
            i &= i - 1
        return s

    # O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    # i + lowbit(i) once complete), then one pass of running prefix sums
    def getAll(self):
        n = self.n
        d = self.tree[:]
        for i in range(n, 0, -1):
            j = i + (i & -i)
            if j <= n:
                d[j] ^= d[i]
        out, s = [], 0
        for i in range(1, n + 1):
            s ^= d[i]
            out.append(s)
        return out

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        d = self.pointGet(i) ^ val
        if d:
            self.rangeXorApply(i, i, d)

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logN) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        cur = self.pointGet(i)
        if val > cur:
            self.rangeXorApply(i, i, cur ^ val)

    # O(logN) -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        cur = self.pointGet(i)
        if val < cur:
            self.rangeXorApply(i, i, cur ^ val)
