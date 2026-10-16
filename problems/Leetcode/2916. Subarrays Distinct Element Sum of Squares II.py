

# TEMPLATE BY https://github.com/agrawalishaan
# You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

# Complexities:
# Build: O(n)
# Space: O(n)
# Query/Update: O(log N)

# baseFn: (val, i) => ...
# combineFn: (leftVal, rightVal, leftLeftIdx, leftRightIdx, rightLeftIdx, rightRightIdx) => ...
# applyLazyToValue: (lazyValue, currentValue) => newValue
# combineLazies: (oldLazy, newLazy) => combinedLazy
# tupleNametags: If baseFn returns a tuple, we can supply nametags for each value, like ('min', 'max'), used for debugging

class LazyPropagationSegmentTree:
    def __init__(self, arr, baseFn, combineFn, applyLazyToValue, combineLazies, tupleNametags=None):
        self.n = len(arr)
        self.arr = arr
        self.tree = [None] * (4 * self.n)
        self.lazy = [None] * (4 * self.n)
        self._combine = combineFn
        self._baseFn = baseFn
        self._applyAggregate = applyLazyToValue
        self._compose = combineLazies
        self.tupleNametags = tupleNametags
        self._build(1, 0, self.n - 1)

    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = self._baseFn(self.arr[tl])
            return
        tm = (tr + tl) // 2
        self._build(2 * i, tl, tm)
        self._build(2 * i + 1, tm + 1, tr)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1])

    def _push(self, i, tl, tr):
        if self.lazy[i] is not None:
            # print(f"Pushing lazy value at node {i} [{tl},{tr}] with lazyValue {self.lazy[i]}")
            left_child = 2 * i
            right_child = 2 * i + 1
            self.tree[i] = self._applyAggregate(self.lazy[i], self.tree[i])
            if tl != tr:
                if self.lazy[left_child] is None:
                    self.lazy[left_child] = self.lazy[i]
                else:
                    self.lazy[left_child] = self._compose(self.lazy[left_child], self.lazy[i])

                if self.lazy[right_child] is None:
                    self.lazy[right_child] = self.lazy[i]
                else:
                    self.lazy[right_child] = self._compose(self.lazy[right_child], self.lazy[i])

            self.lazy[i] = None

    def _updateRange(self, i, tl, tr, l, r, lazyValue):
        # print(f"Updating range [{l},{r}] with lazyValue {lazyValue} at node {i} [{tl},{tr}]")
        self._push(i, tl, tr)
        if l > tr or r < tl:
            return  # No overlap
        if l <= tl and tr <= r:
            self.lazy[i] = lazyValue
            self._push(i, tl, tr)
            return
        tm = (tl + tr) // 2
        self._updateRange(2 * i, tl, tm, l, r, lazyValue)
        self._updateRange(2 * i + 1, tm + 1, tr, l, r, lazyValue)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1])

    def _queryRecurse(self, i, tl, tr, l, r):
        # print(f"Querying range [{l},{r}] at node {i} [{tl},{tr}]")
        self._push(i, tl, tr)
        if l > tr or r < tl:
            return None  # No overlap
        if l <= tl and tr <= r:
            # print(f"Fully in bounds, returning node value: {self.tree[i]}")
            return self.tree[i]
        tm = (tl + tr) // 2
        if l > tm:
            # print(f"Left child [{tl},{tm}] would have no overlap, so only using right")
            return self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        elif r < tm + 1:
            # print(f"Right child [{tm+1},{tr}] would have no overlap, so only using left")
            return self._queryRecurse(2 * i, tl, tm, l, r)

        leftResult = self._queryRecurse(2 * i, tl, tm, l, r)
        rightResult = self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        combinedResult = self._combine(leftResult, rightResult, max(l, tl), min(tm, r), max(l, tm + 1), min(r, tr))
        # print(f"Combining results for parent [{tl},{tr}] for query [{l},{r}]: left useful: {leftResult}, right useful: {rightResult} -> combined useful: {combinedResult}")
        return combinedResult

    def updateRange(self, l, r, lazyValue):
        self._updateRange(1, 0, self.n - 1, l, r, lazyValue)

    def query(self, l, r):
        return self._queryRecurse(1, 0, self.n - 1, l, r)

# every node holds (width, sumAllUniq, sumAllUniqSquared)
# sumAllUniq is the sum of distinct elements in a subarray l...i for all tl<=l<=tr
# sumAllUniqSquared is the sum of all of those terms individually squared
def base(v):
    return 1, 0, 0

def agg(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def applyLazyToValue(lazyVal, tup):
    width, sumAllUniq, sumAllUniqSquared = tup
    nSumAllUniq = sumAllUniq + (lazyVal * width)
    nSumAllUniqSquared = sumAllUniqSquared + (2 * lazyVal * sumAllUniq) + (lazyVal * lazyVal * width)
    return width, nSumAllUniq, nSumAllUniqSquared

def combineLazies(a, b):
    return a + b

class Solution:
    def sumCounts(self, nums: List[int]) -> int:
        arr = [0] * len(nums)
        seg = LazyPropagationSegmentTree(arr, base, agg, applyLazyToValue, combineLazies)
        prev = {} # maps val to prev index
        MOD = 10**9 + 7
        res = 0
        for i, v in enumerate(nums):
            if v not in prev:
                seg.updateRange(0, i, 1)
            else:
                seg.updateRange(prev[v] + 1, i, 1)
            
            prev[v] = i
            res += seg.query(0, len(nums) - 1)[2]
            
        return res % MOD
        