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

class Solution:
    def maxProfit(self, prices: List[int], profits: List[int]) -> int:
        uniquePrices = sorted(set(prices))
        priceCmp = {price : i for i, price in enumerate(uniquePrices)}
        # for each price, I want the max profit we can get if we stay <= that price with 1 previous purchase

        #  now for each price, I want the max profit we can get if we stay <= that price with 2 purchases

        # lets make dp1[price] mean the max profit we can get where the last purchase was exactly price
        # so we do a range max query

        mx = len(priceCmp)

        dp1 = MaxSegTree([-inf] * (mx + 1))
        dp2 = MaxSegTree([-inf] * (mx + 1))
        res = -inf

        for price, profit in zip(prices, profits):
            compressed = priceCmp[price]
            # we could stack this onto 2 existing purchases
            prevBest = dp2.queryMax(0, compressed - 1) if compressed else -inf
            nTriple = prevBest + profit
            res = max(res, nTriple)

            # we could stack this onto 1 existing purchase to make 2
            prevSingle = dp1.queryMax(0, compressed - 1) if compressed else -inf
            nDouble = prevSingle + profit
            currDouble = dp2.queryMax(compressed, compressed)
            if nDouble > currDouble:
                dp2.pointUpdateAndMutateArray(compressed, nDouble)

            # we could buy this outright as one
            curr = dp1.queryMax(compressed, compressed)
            if profit > curr:
                dp1.pointUpdateAndMutateArray(compressed, profit)
        
        return res if res != -inf else -1