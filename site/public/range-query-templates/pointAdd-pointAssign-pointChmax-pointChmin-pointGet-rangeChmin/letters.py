# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeChmin/letters.py
# @operations: getAll pointAssign pointChmax pointChmin pointGet rangeChmin
# @data-structure-type: seg-tree
# @complexities:
#   getAll: N
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: 1
#   pointGet: log(N)
#   rangeChmin: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: tree[1*N]
#   tags: tree[1*N]
#   other: none
#   note: tree[n:] holds the values, tree[1:n] holds each node's pending rangeChmin tag (no aggregates); leaves count as node data, internal nodes as tags

# Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
# operations that make sense on characters are listed.
# rangeChmin + point ops with no range aggregates. All indices 0-based, ranges inclusive [l, r].
# rangeChmin composes with itself in any order, so a range update only tags the O(logN) covering nodes and pointGet
# folds the tags on the leaf-to-root path. Only pointAssign-style overwrites need to push those tags off the path first,
# because they must not be re-applied to the new value.
class RangeChminTree:
    __slots__ = ("n", "tree")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.tree = [chr(0x10FFFF)] * n + list(arr)

    # O(logN) -- a[i] = min(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmin(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        tree = self.tree
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                tree[l] = tree[l] if tree[l] < v else v
                l += 1
            if r & 1:
                r -= 1
                tree[r] = tree[r] if tree[r] < v else v
            l >>= 1
            r >>= 1

    # O(logN) -- move the tags on i's root-to-leaf path down, so nothing above i is pending
    def _push(self, p):
        tree = self.tree
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            t = tree[x]
            if t != chr(0x10FFFF):
                y = x << 1
                tree[y] = tree[y] if tree[y] < t else t
                tree[y | 1] = tree[y | 1] if tree[y | 1] < t else t
                tree[x] = chr(0x10FFFF)

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        tree = self.tree
        p = i + self.n
        a = tree[p]
        p >>= 1
        while p:
            t = tree[p]
            a = a if a < t else t
            p >>= 1
        return a

    # O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    # each node's tag is complete when it is pushed), then read the leaves
    def getAll(self):
        tree = self.tree
        for x in range(1, self.n):
            t = tree[x]
            if t != chr(0x10FFFF):
                y = x << 1
                tree[y] = tree[y] if tree[y] < t else t
                tree[y | 1] = tree[y | 1] if tree[y | 1] < t else t
                tree[x] = chr(0x10FFFF)
        return self.tree[self.n:]

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        self.tree[p] = val

    # O(logN) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        if val > self.tree[p]:
            self.tree[p] = val

    # O(1) -- a[i] = min(a[i], val); a leaf-level chmin tag commutes with the pending ones above it; needs 0 <= i < n,
    # else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        if val < self.tree[p]:
            self.tree[p] = val
