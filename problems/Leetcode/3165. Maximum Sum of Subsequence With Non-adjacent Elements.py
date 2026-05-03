# _____________________________________________________
# TEMPLATE BY https://github.com/agrawalishaan
# You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

# Complexities:
# Build: O(n)
# Space: O(n)
# Query range O(logN)
# Update value O(logN)

# Inputs into constructor
# arr: array of data
# baseFn: The default value of a leaf node. Can be anything, usually a single value or a tuple of data
# combineFn: The way to aggregate data from two children nodes. For instance in a sum segment tree, combineFn would be: lambda a, b: a + b. The combineFn is by default a function with 6 arguments: a, b, aLeftIdx, aRightIdx, bLeftIdx, bRightIdx - to change this to just a and b, remove the last 4 arguments from all invocations
# tupleNametags - if baseFn returns a tuple, we can supply nametags for each value, used for print debugging


# Common use cases:
# SUM SEGMENT TREE:
# combineFn = lambda a, b: a + b
# baseFn = lambda val: val

# MAX SEGMENT TREE:
# combineFn = lambda a, b: max(a, b)
# baseFn = lambda val: val

# MIN SEGMENT TREE:
# combineFn = lambda a, b: min(a, b)
# baseFn = lambda val: val

class SegmentTree:
    def __init__(self, arr, baseFn, combine, tupleNametags=None):
        self.n = len(arr)
        self.arr = arr
        self.tree = [None] * (4 * self.n)
        self._combine = combine
        self._baseFn = baseFn
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

    def _queryRecurse(self, i, tl, tr, l, r):
        if l <= tl and tr <= r:
            return self.tree[i]

        tm = (tl + tr) // 2

        # if a child has no overlap
        if l > tm:
            return self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        elif r < tm + 1:
            return self._queryRecurse(2 * i, tl, tm, l, r)

        leftResult = self._queryRecurse(2 * i, tl, tm, l, r)
        rightResult = self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        combinedResult = self._combine(leftResult, rightResult)
        return combinedResult

    def _updateRecurse(self, i, tl, tr, posToBeUpdated):
        if tl == tr:
            self.tree[i] = self._baseFn(self.arr[tl])
            return
        tm = (tl + tr) // 2
        if posToBeUpdated <= tm:
            self._updateRecurse(2 * i, tl, tm, posToBeUpdated)
        else:
            self._updateRecurse(2 * i + 1, tm + 1, tr, posToBeUpdated)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1])


    ################ PUBLIC METHODS START HERE ################

    def updateAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        self._updateRecurse(1, 0, self.n - 1, index)

    def query(self, l, r):
        return self._queryRecurse(1, 0, self.n - 1, l, r)

class Solution:
    def maximumSumSubsequence(self, nums: List[int], queries: List[List[int]]) -> int:
        # each value stores (max, maxL, maxLR, maxR)
        def baseFn(val):
            return (0, 0, val, 0)
        
        def combine(a, b):
            aMax, aMaxL, aMaxLR, aMaxR = a
            bMax, bMaxL, bMaxLR, bMaxR = b

            # compute new max, can't use L from `a` or R from `b`
            # add aMaxR with bMax
            newMax = aMaxR + bMax
            # add aMax with bMax
            newMax = max(newMax, aMax + bMax)
            # add aMax with bMaxL
            newMax = max(newMax, aMax + bMaxL)

            # compute new maxL
            # add aMaxL with bMaxL
            newMaxL = aMaxL + bMaxL
            # add aMaxLR with bMax
            newMaxL = max(newMaxL, aMaxLR + bMax)
            # add aMaxL with bMax
            newMaxL = max(newMaxL, aMaxL + bMax)

            # compute new maxLR
            # add aMaxL with bMaxLR
            newMaxLR = aMaxL + bMaxLR
            # add aMaxL with bMaxR
            newMaxLR = max(newMaxLR, aMaxL + bMaxR)
            # add aMaxLR with bMaxR
            newMaxLR = max(newMaxLR, aMaxLR + bMaxR)

            # compute new maxR
            # add aMax with bMaxR
            newMaxR = aMax + bMaxR
            # add aMax with bMaxLR
            newMaxR = max(newMaxR, aMax + bMaxLR)
            # add aMaxR with bMaxR
            newMaxR = max(newMaxR, aMaxR + bMaxR)

            return (newMax, newMaxL, newMaxLR, newMaxR)
        
        st = SegmentTree(nums, baseFn, combine)

        res = 0
        for pos, x in queries:
            st.updateAndMutateArray(pos, x)
            query = st.query(0, len(nums) - 1)
            res += max(query)

        return res % (10**9 + 7)



            
