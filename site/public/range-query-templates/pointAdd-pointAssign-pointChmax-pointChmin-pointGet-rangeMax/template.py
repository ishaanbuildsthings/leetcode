# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeMax
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   rangeMax: log(N)
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

    # 0 if l>r
    def rangeMax(self, l, r):
        if l > r: return 0
        return self._queryHalfOpen(l, r + 1)

    # Point overwrite: a[index] = newVal. Only updates the tree; the array you passed in is untouched.
    def pointAssign(self, index, newVal):
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

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.tree[self.size + i]

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.tree[self.size + i]:
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.tree[self.size + i]:
            self.pointAssign(i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.tree[self.size + i] + delta)