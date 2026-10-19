# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAndApply: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: none
#   tags: tree[2*N]
#   other: none
#   note: tree[n:] holds the values, tree[1:n] holds each node's pending rangeAndApply tag (no aggregates)

# rangeAndApply + point ops with no range aggregates. All indices 0-based, ranges inclusive [l, r].
# rangeAndApply composes with itself in any order, so a range update only tags the O(logN) covering nodes and
# pointGet folds the tags on the leaf-to-root path. Only pointAssign-style overwrites need to push those
# tags off the path first, because they must not be re-applied to the new value.
class RangeAndTree:
    __slots__ = ("n", "tree")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.tree = [-1] * n + list(arr)

    # O(logN) -- a[i] &= x for i in [l, r]
    def rangeAndApply(self, l, r, x):
        tree = self.tree
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                tree[l] = tree[l] & x
                l += 1
            if r & 1:
                r -= 1
                tree[r] = tree[r] & x
            l >>= 1
            r >>= 1

    # O(logN) -- move the tags on i's root-to-leaf path down, so nothing above i is pending
    def _push(self, p):
        tree = self.tree
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            t = tree[x]
            if t != -1:
                y = x << 1
                tree[y] = tree[y] & t
                tree[y | 1] = tree[y | 1] & t
                tree[x] = -1

    # O(logN) -- a[i]
    def pointGet(self, i):
        tree = self.tree
        p = i + self.n
        a = tree[p]
        p >>= 1
        while p:
            t = tree[p]
            a = a & t
            p >>= 1
        return a

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        p = i + self.n
        self._push(p)
        self.tree[p] = val

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        p = i + self.n
        self._push(p)
        self.tree[p] = (self.tree[p] + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        p = i + self.n
        self._push(p)
        if val > self.tree[p]:
            self.tree[p] = val

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        p = i + self.n
        self._push(p)
        if val < self.tree[p]:
            self.tree[p] = val
