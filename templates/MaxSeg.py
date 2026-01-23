# ⚠️ Not fully benchmarked but should be pretty fast, 2n iterative tree
# ⚠️ Missing functions like leftmost > X, rightmost > X, etc
# ✅ Passed https://codeforces.com/contest/2031/submission/359281416
class MaxSegTree:
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)

        size = 1
        while size < self.n:
            size <<= 1
        self.size = size

        tree = [float("-inf")] * (2 * size)
        base = size
        for i, v in enumerate(arr):
            tree[base + i] = v
        for idx in range(size - 1, 0, -1):
            left = tree[idx << 1]
            right = tree[(idx << 1) | 1]
            tree[idx] = left if left >= right else right
        self.tree = tree

    def _queryHalfOpen(self, l, r):
        tree = self.tree
        l += self.size
        r += self.size
        ans = float("-inf")
        while l < r:
            if l & 1:
                v = tree[l]
                ans = v if v >= ans else ans
                l += 1
            if r & 1:
                r -= 1
                v = tree[r]
                ans = v if v >= ans else ans
            l >>= 1
            r >>= 1
        return ans

    def queryMax(self, l, r):
        return self._queryHalfOpen(l, r + 1)

    def pointUpdateAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        tree = self.tree
        pos = self.size + index
        tree[pos] = newVal
        pos >>= 1
        while pos:
            left = tree[pos << 1]
            right = tree[(pos << 1) | 1]
            tree[pos] = left if left >= right else right
            pos >>= 1
