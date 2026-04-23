# ⚠️ Not fully benchmarked but should be pretty fast, 2n iterative tree
class SumSegTree:
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)

        size = 1
        while size < self.n:
            size <<= 1
        self.size = size

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

    def querySum(self, l, r):
        return self._queryHalfOpen(l, r + 1)

    def pointUpdateAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        tree = self.tree
        pos = self.size + index
        tree[pos] = newVal
        pos >>= 1
        while pos:
            tree[pos] = tree[pos << 1] + tree[(pos << 1) | 1]
            pos >>= 1