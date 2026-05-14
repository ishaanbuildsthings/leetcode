# https://leetcode.com/problems/wiggle-subsequence/description/
# difficulty: medium
# tags: dynamic programming 2d, greedy

# Problem
# A wiggle sequence is a sequence where the differences between successive numbers strictly alternate between positive and negative. The first difference (if one exists) may be either positive or negative. A sequence with one element and a sequence with two non-equal elements are trivially wiggle sequences.

# For example, [1, 7, 4, 9, 2, 5] is a wiggle sequence because the differences (6, -3, 5, -7, 3) alternate between positive and negative.
# In contrast, [1, 4, 7, 2, 5] and [1, 7, 4, 5, 5] are not wiggle sequences. The first is not because its first two differences are positive, and the second is not because its last difference is zero.
# A subsequence is obtained by deleting some elements (possibly zero) from the original sequence, leaving the remaining elements in their original order.

# Given an integer array nums, return the length of the longest wiggle subsequence of nums.

# Solution
# I just did a DP with the previous number and direction. There is an O(n) greedy, I would have to think about it. Time and space: O(n^2)

class Solution:
    def wiggleMaxLength(self, nums: List[int]) -> int:
        @cache
        def dp(i, prev, newDirection): # 1 means go up for new direction
            # base case
            if i == len(nums):
                return 0

            resForThis = 0

            # we can take the current number if we adhere to the property
            if newDirection and nums[i] > prev:
                resForThis = 1 + dp(i + 1, nums[i], 0)
            elif not newDirection and nums[i] < prev:
                resForThis = 1 + dp(i + 1, nums[i], 1)

            # we can always skip the number
            resForThis = max(resForThis, dp(i + 1, prev, newDirection))

            return resForThis

        return max(
            dp(0, float('-inf'), 1),
            dp(0, float('inf'), 0)
        )



