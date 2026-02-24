# ⚠️ Not fully benchmarked but should be pretty fast, 2n iterative tree
# Mirror of MaxSegTree with min operations
class MinSegTree:
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)

        size = 1
        while size < self.n:
            size <<= 1
        self.size = size

        tree = [float("inf")] * (2 * size)
        base = size
        for i, v in enumerate(arr):
            tree[base + i] = v
        for idx in range(size - 1, 0, -1):
            left = tree[idx << 1]
            right = tree[(idx << 1) | 1]
            tree[idx] = left if left <= right else right
        self.tree = tree

    def _queryHalfOpen(self, l, r):
        tree = self.tree
        l += self.size
        r += self.size
        ans = float("inf")
        while l < r:
            if l & 1:
                v = tree[l]
                ans = v if v <= ans else ans
                l += 1
            if r & 1:
                r -= 1
                v = tree[r]
                ans = v if v <= ans else ans
            l >>= 1
            r >>= 1
        return ans

    def queryMin(self, l, r):
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
            tree[pos] = left if left <= right else right
            pos >>= 1

    # returns -1 if nothing in range
    def leftmostLteX(self, l, r, x):
        return self._leftmostLteX(1, 0, self.size - 1, l, r, x)

    def _leftmostLteX(self, node, nodeL, nodeR, l, r, x):
        if nodeR < l or nodeL > r or self.tree[node] > x:
            return -1
        if nodeL == nodeR:
            return nodeL
        mid = (nodeL + nodeR) >> 1
        left = self._leftmostLteX(node << 1, nodeL, mid, l, r, x)
        if left != -1:
            return left
        return self._leftmostLteX((node << 1) | 1, mid + 1, nodeR, l, r, x)

    # returns -1 if nothing in range
    def rightmostLteX(self, l, r, x):
        return self._rightmostLteX(1, 0, self.size - 1, l, r, x)

    def _rightmostLteX(self, node, nodeL, nodeR, l, r, x):
        if nodeR < l or nodeL > r or self.tree[node] > x:
            return -1
        if nodeL == nodeR:
            return nodeL
        mid = (nodeL + nodeR) >> 1
        right = self._rightmostLteX((node << 1) | 1, mid + 1, nodeR, l, r, x)
        if right != -1:
            return right
        return self._rightmostLteX(node << 1, nodeL, mid, l, r, x)