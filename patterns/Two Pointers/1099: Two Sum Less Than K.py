# https://leetcode.com/problems/two-sum-less-than-k/description/
# difficulty: easy
# tags: two pointers, segment tree, fractional cascading, merge sort tree

# Problem
# Given an array nums of integers and integer k, return the maximum sum such that there exists i < j with nums[i] + nums[j] = sum and sum < k. If no i, j exist satisfying this equation, return -1.

# Solution, we can solve this with two pointers, but I built a merge sort tree that solves the "largest number <= a threhsold in a subarray" and did a log^2n query. We can speed this up with fractional cascading.

IDENTITY = float('-inf') # combine(a, IDENTITY) is always a
class LargestLTEThreshold:

    def __init__(self, data):
        self.n = len(data)
        self.data = data
        self.tree = [None] * 4 * self.n
        self._build(1, 0, self.n - 1)

    def _basefn(self, val):
      return [val] # returns a sorted list

    def _build(self, i, tl, tr):
        # base case
        if tl == tr:
            self.tree[i] = self._basefn(self.data[tl])
            return
        tm = (tr + tl) // 2
        self._build(2*i, tl, tm)
        self._build(2*i + 1, tm + 1, tr)
        self.tree[i] = self._combine(self.tree[2*i], self.tree[2*i + 1])

    def _combine(self, a, b):
        newList = []
        i = 0
        j = 0
        while i < len(a) and j < len(b):
            if a[i] <= b[j]:
                newList.append(a[i])
                i += 1
            else:
                newList.append(b[j])
                j += 1
        if i < len(a):
            for k in range(i, len(a)):
                newList.append(a[k])
        if j < len(b):
            for g in range(j, len(b)):
                newList.append(b[g])
        return newList

    def _queryRecurse(self, i, tl, tr, l, r, threshold):
        # if we are contained, get the largest number <= a threshold
        if tl >= l and tr <= r:
            idx = bisect.bisect_right(self.tree[i], threshold)
            if idx == 0:
                return float('-inf')
            return self.tree[i][idx - 1]

        # if we have no intersection
        if tr < l or tl > r:
            return IDENTITY

        tm = (tr + tl) // 2 # calculate the middle of our node, basically get the two children
        resultLeft = self._queryRecurse(2*i, tl, tm, l, r, threshold)
        resultRight = self._queryRecurse(2*i + 1, tm + 1, tr, l, r, threshold)
        return max(resultLeft, resultRight)

    def query(self, l, r, threshold) -> int:
        return self._queryRecurse(1, 0, self.n - 1, l, r, threshold)

class Solution:
    def twoSumLessThanK(self, nums: List[int], k: int) -> int:
        seg = LargestLTEThreshold(nums)
        res = float('-inf')
        for i in range(len(nums)):
            maxAllowed = k - nums[i] - 1
            res = max(res, nums[i] + seg.query(i + 1, len(nums) - 1, maxAllowed))
        return res if res != float('-inf') else -1
