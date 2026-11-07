# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeMax/template.py
# @operations: getAll maxAll pointAdd pointAssign pointChmax pointChmin pointGet rangeMax
# @data-structure-type: seg-tree
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   rangeMax: log(N)
#   maxAll: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: tree[2*N]
#   tags: none
#   other: none
#   note: tree holds each node's max; leaves are tree[n..2n), no power-of-two padding; arr is a reference
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/pointAssignRangeMax.py

from math import inf
class MaxSegTree:
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        size = self.size = self.n  # 2N layout: leaves live at tree[n..2n)
        tree = [-inf] * (2 * size)
        base = size
        for i, v in enumerate(arr):
            tree[base + i] = v
        for idx in range(size - 1, 0, -1):
            tree[idx] = max(tree[idx << 1], tree[(idx << 1) | 1])
        self.tree = tree

    def _queryHalfOpen(self, l, r):
        tree = self.tree
        l += self.size
        r += self.size
        ans = -inf
        while l < r:
            if l & 1:
                if tree[l] > ans: ans = tree[l]
                l += 1
            if r & 1:
                r -= 1
                if tree[r] > ans: ans = tree[r]
            l >>= 1
            r >>= 1
        return ans

    # O(logN) -- max of a[l..r] (0 if l > r); needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r: return 0
        return self._queryHalfOpen(l, r + 1)

    # Point overwrite: a[index] = newVal. Only updates the tree; the array you passed in is untouched.; needs
    # 0 <= index < n, else IndexError
    def pointAssign(self, index, newVal):
        if not 0 <= index < self.n:
            raise IndexError(f"pointAssign: needs 0 <= index < n, got index = {index}, n = {self.n}")
        tree = self.tree
        pos = self.size + index
        tree[pos] = newVal
        pos >>= 1
        while pos:
            new = max(tree[pos << 1], tree[(pos << 1) | 1])
            if tree[pos] == new:
                break
            tree[pos] = new
            pos >>= 1

    # Same as pointAssign, but also writes newVal into the array you passed in.
    def pointAssignAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        self.pointAssign(index, newVal)

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.tree[self.size + i]

    # O(N) -- the whole array (a copy of the leaves)
    def getAll(self):
        return self.tree[self.size:self.size + self.n]

    # a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.tree[self.size + i]:
            self.pointAssign(i, val)

    # a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.tree[self.size + i]:
            self.pointAssign(i, val)

    # a[i] += delta; needs needs 0 <= i < n, else IndexError, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")

    # O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.n < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.n - 1)
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.tree[self.size + i] + delta)