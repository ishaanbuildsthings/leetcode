# https://leetcode.com/problems/paint-fence/description/
# difficulty: medium
# tags: dynamic programming 2d

# Problem
# You are painting a fence of n posts with k different colors. You must paint the posts following these rules:

# Every post must be painted exactly one color.
# There cannot be three or more consecutive posts with the same color.
# Given the two integers n and k, return the number of ways you can paint the fence.

# Solution
# If we are at a fence we can see how many previous colors we have in a row and determine what to do. I think there is a more clever way where we don't need to store the # of previous colors in a row, maybe just by skipping forward a certain amount of indices. Should also be an O(1) space solution.

class Solution:
    def numWays(self, n: int, k: int) -> int:

        @cache
        def dp(i, lastConsecutive):
            # base case
            if i == n:
                return 1

            if lastConsecutive == 0:
                return k * dp(i + 1, 1)

            elif lastConsecutive == 1:
                return (k - 1) * dp(i + 1, 1) + dp(i + 1, 2)

            return (k - 1) * dp(i + 1, 1)

        return dp(0, 0)

