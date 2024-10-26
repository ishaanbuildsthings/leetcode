# https://leetcode.com/problems/number-of-ways-to-split-array/description/
# Difficulty: Medium
# tags: prefix, postfix

# Problem

# You are given a 0-indexed integer array nums of length n.

# nums contains a valid split at index i if the following are true:

# The sum of the first i + 1 elements is greater than or equal to the sum of the last n - i - 1 elements.
# There is at least one element to the right of i. That is, 0 <= i < n - 1.
# Return the number of valid splits in nums.

# Solution, we can just track the left sum and right sum in O(1) and shift accordingly. I wasn't thinking and am trying to speedrun to 1000 so I wrote an O(n) space solution at first. O(n) time.

class Solution:
    def waysToSplitArray(self, nums: List[int]) -> int:
        prefixSums = []
        runningSum = 0
        for num in nums:
            runningSum += num
            prefixSums.append(runningSum)

        def rangeQuery(l, r):
            return prefixSums[r] - (prefixSums[l - 1] if l > 0 else 0)

        res = 0
        for splitLeft in range(len(nums) - 1):
            leftSum = prefixSums[splitLeft]
            rightSum = rangeQuery(splitLeft + 1, len(nums) - 1)
            res += leftSum >= rightSum

        return res