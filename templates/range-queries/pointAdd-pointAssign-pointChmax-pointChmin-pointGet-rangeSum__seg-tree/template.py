# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: tree[2*N]
#   tags: none
#   other: none
#   note: tree holds each node's sum; leaves are tree[n..2n), no power-of-two padding; arr is a reference
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/pointAssignRangeSum.py

# ⚠️ Not fully benchmarked but should be pretty fast, 2n iterative tree
class SumSegTree:
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)

        size = self.size = self.n  # 2N layout: leaves live at tree[n..2n)

        tree = [0] * (2 * size)
        base = size
        for i, v in enumerate(arr):
            tree[base + i] = v
        for idx in range(size - 1, 0, -1):
            tree[idx] = tree[idx << 1] + tree[(idx << 1) | 1]
        self.tree = tree

    def _queryHalfOpen(self, l, r):
        tree = self.tree
        l += self.size
        r += self.size
        ans = 0
        while l < r:
            if l & 1:
                ans += tree[l]
                l += 1
            if r & 1:
                r -= 1
                ans += tree[r]
            l >>= 1
            r >>= 1
        return ans

    def rangeSum(self, l, r):
        return self._queryHalfOpen(l, r + 1)

    # Point overwrite: a[index] = newVal. Only updates the tree; the array you passed in is untouched.
    def pointAssign(self, index, newVal):
        tree = self.tree
        pos = self.size + index
        tree[pos] = newVal
        pos >>= 1
        while pos:
            tree[pos] = tree[pos << 1] + tree[(pos << 1) | 1]
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
        tree = self.tree
        pos = self.size + i
        while pos:
            tree[pos] += delta
            pos >>= 1