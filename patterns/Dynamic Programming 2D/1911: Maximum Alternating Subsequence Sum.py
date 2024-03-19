# https://leetcode.com/problems/maximum-alternating-subsequence-sum/description/
# difficulty: medium
# tags: dynamic programming 2d

# Problem
# The alternating sum of a 0-indexed array is defined as the sum of the elements at even indices minus the sum of the elements at odd indices.

# For example, the alternating sum of [4,2,5,3] is (4 + 5) - (2 + 3) = 4.
# Given an array nums, return the maximum alternating sum of any subsequence of nums (after reindexing the elements of the subsequence).

# A subsequence of an array is a new array generated from the original array by deleting some elements (possibly none) without changing the remaining elements' relative order. For example, [2,7,4] is a subsequence of [4,2,3,7,2,1,4] (the underlined elements), while [2,4,2] is not.

# Solutionm O(n) time O(n) space, can prob do O(1) space

class Solution:
    def maxAlternatingSum(self, nums: List[int]) -> int:
        # could prob do O(1) space

        @cache
        def dp(i, nextIsAdd):
            # base
            if i == len(nums):
                return 0

            # if we take this number
            resThis = dp(i + 1, not nextIsAdd) + (nums[i] if nextIsAdd else -1 * nums[i])

            # if we skip
            resThis = max(resThis, dp(i + 1, nextIsAdd))

            return resThis

        return max(dp(0, True), dp(0, False))
