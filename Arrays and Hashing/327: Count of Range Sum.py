# https://leetcode.com/problems/count-of-range-sum/
# difficulty: hard
# tags: avl tree, binary search, segment tree, lop off

# Problem
# Given an integer array nums and two integers lower and upper, return the number of range sums that lie in [lower, upper] inclusive.

# Range sum S(i, j) is defined as the sum of the elements in nums between indices i and j inclusive, where i <= j.

# Solution, O(n log n) time, O(n) space
# I just used a sorted list on the prefix sums to see how many I could lop off. We could prune by tracking the max and min and foregoing a log n operation if nothing of adequate size exists.

import sortedcontainers

class Solution:
    def countRangeSum(self, nums: List[int], lower: int, upper: int) -> int:
        prefixSums = sortedcontainers.SortedList()
        prefixSums.add(0) # we can always cut off nothing
        runningPrefix = 0

        res = 0
        for i in range(len(nums)):
            minToCutOff = (runningPrefix + nums[i]) - upper
            maxToCutOff = (runningPrefix + nums[i]) - lower
            countSmallerThanMin = prefixSums.bisect_left(minToCutOff)
            countBiggerThanMax = len(prefixSums) - prefixSums.bisect_right(maxToCutOff)
            res += len(prefixSums) - (countSmallerThanMin + countBiggerThanMax)
            runningPrefix += nums[i]
            prefixSums.add(runningPrefix)
        return res
