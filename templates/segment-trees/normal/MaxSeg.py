# ⚠️ Not fully benchmarked but should be pretty fast, 2n iterative tree
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

    # returns -1 if nothing in range
    def leftmostGteX(self, l, r, x):
            return self._leftmostGteX(1, 0, self.size - 1, l, r, x)

    def _leftmostGteX(self, node, nodeL, nodeR, l, r, x):
        if nodeR < l or nodeL > r or self.tree[node] < x:
            return -1
        if nodeL == nodeR:
            return nodeL
        mid = (nodeL + nodeR) >> 1
        left = self._leftmostGteX(node << 1, nodeL, mid, l, r, x)
        if left != -1:
            return left
        return self._leftmostGteX((node << 1) | 1, mid + 1, nodeR, l, r, x)

    # returns -1 if nothing in range
    def rightmostGteX(self, l, r, x):
        return self._rightmostGteX(1, 0, self.size - 1, l, r, x)

    def _rightmostGteX(self, node, nodeL, nodeR, l, r, x):
        if nodeR < l or nodeL > r or self.tree[node] < x:
            return -1
        if nodeL == nodeR:
            return nodeL
        mid = (nodeL + nodeR) >> 1
        right = self._rightmostGteX((node << 1) | 1, mid + 1, nodeR, l, r, x)
        if right != -1:
            return right
        return self._rightmostGteX(node << 1, nodeL, mid, l, r, x)