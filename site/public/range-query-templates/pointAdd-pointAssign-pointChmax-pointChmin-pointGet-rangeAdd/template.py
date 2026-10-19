# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   build: N
# @memory:
#   layout: none
#   node: tree[1*N]
#   tags: none
#   other: none
#   note: a Fenwick tree over the difference array; a[i] is the prefix sum of differences up to i

# Range add, point get. All indices 0-based, ranges inclusive [l, r].
class RangeAddBIT:
    __slots__ = ("n", "tree")

    # O(N) -- linear Fenwick build over a[i] - a[i - 1]
    def __init__(self, arr):
        n = self.n = len(arr)
        tree = self.tree = [0] * (n + 1)
        prev = 0
        for i in range(1, n + 1):
            v = arr[i - 1]
            tree[i] += v - prev
            prev = v
            j = i + (i & -i)
            if j <= n:
                tree[j] += tree[i]

    def _add(self, i, v):
        tree, n = self.tree, self.n
        i += 1
        while i <= n:
            tree[i] += v
            i += i & -i

    # O(logN) -- a[i] for i in [l, r] += v
    def rangeAdd(self, l, r, v):
        self._add(l, v)
        if r + 1 < self.n:
            self._add(r + 1, -v)

    # O(logN) -- a[i]
    def pointGet(self, i):
        tree = self.tree
        s = 0
        i += 1
        while i:
            s += tree[i]
            i &= i - 1
        return s

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
