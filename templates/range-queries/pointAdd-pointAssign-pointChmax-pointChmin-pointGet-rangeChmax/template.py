# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeChmax/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeChmax
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: 1
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeChmax: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: tree[1*N]
#   tags: tree[1*N]
#   other: none
#   note: tree[n:] holds the values, tree[1:n] holds each node's pending rangeChmax tag (no aggregates); leaves count as node data, internal nodes as tags

# rangeChmax + point ops with no range aggregates. All indices 0-based, ranges inclusive [l, r].
# rangeChmax composes with itself in any order, so a range update only tags the O(logN) covering nodes and
# pointGet folds the tags on the leaf-to-root path. Only pointAssign-style overwrites need to push those
# tags off the path first, because they must not be re-applied to the new value.
class RangeChmaxTree:
    __slots__ = ("n", "tree")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.tree = [float("-inf")] * n + list(arr)

    # O(logN) -- a[i] = max(a[i], v) for i in [l, r]
    def rangeChmax(self, l, r, v):
        tree = self.tree
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                tree[l] = tree[l] if tree[l] > v else v
                l += 1
            if r & 1:
                r -= 1
                tree[r] = tree[r] if tree[r] > v else v
            l >>= 1
            r >>= 1

    # O(logN) -- move the tags on i's root-to-leaf path down, so nothing above i is pending
    def _push(self, p):
        tree = self.tree
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            t = tree[x]
            if t != float("-inf"):
                y = x << 1
                tree[y] = tree[y] if tree[y] > t else t
                tree[y | 1] = tree[y | 1] if tree[y | 1] > t else t
                tree[x] = float("-inf")

    # O(logN) -- a[i]
    def pointGet(self, i):
        tree = self.tree
        p = i + self.n
        a = tree[p]
        p >>= 1
        while p:
            t = tree[p]
            a = a if a > t else t
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

    # O(1) -- a[i] = max(a[i], val); a leaf-level chmax tag commutes with the pending ones above it
    def pointChmax(self, i, val):
        p = i + self.n
        if val > self.tree[p]:
            self.tree[p] = val

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        p = i + self.n
        self._push(p)
        if val < self.tree[p]:
            self.tree[p] = val
