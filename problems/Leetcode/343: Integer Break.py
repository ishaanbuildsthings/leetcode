# https://leetcode.com/problems/integer-break/description/?envType=daily-question&envId=2023-10-06
# difficulty: medium
# tags: dynamic programming 2d

# problem
# Given an integer n, break it into the sum of k positive integers, where k >= 2, and maximize the product of those integers.

# Return the maximum product you can get.

# Solution, O(n^2 * 2) time, O(2n) space
# At first I tried a math deduction, which I believe is possible, but I couldn't quickly figure it out. I resorted to dp. Just try splitting everything. I'm definitely overfit on DP and need to become better at using other tools. In the DP I tracked if a split was yet made to avoid certain edge cases, but I think this is further avoided by bringing edge cases outside the DP function.


class Solution:
    def integerBreak(self, n: int) -> int:
        # 11 -> 3 * 3 * 3 * 2

        # returns the answer for a subproblem
        @cache
        def dp(num, madeSplit):
            # base case
            if num == 1:
                return 1
            resForThis = num if madeSplit else 1
            for split in range(2, num):
                leftPortion = split
                rightPortion = num - split
                ifSplitHere = split * dp(rightPortion, True)
                resForThis = max(resForThis, ifSplitHere)
            return resForThis
        return dp(n, False)