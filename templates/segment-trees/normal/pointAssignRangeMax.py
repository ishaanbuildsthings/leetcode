from math import inf
class MaxSegTree:
    def __init__(self, arr):
        self.arr = list(arr)
        self.n = len(arr)
        size = 1
        while size < self.n:
            size <<= 1
        self.size = size
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
    def queryMax(self, l, r):
        if l > r: return 0
        return self._queryHalfOpen(l, r + 1)

    def pointAssignAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
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