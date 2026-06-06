# https://leetcode.com/problems/max-dot-product-of-two-subsequences/
# Difficulty: Hard
# Tags: dynamic programming 2d

# Problem
# Given two arrays nums1 and nums2.

# Return the maximum dot product between non-empty subsequences of nums1 and nums2 with the same length.

# A subsequence of a array is a new array which is formed from the original array by deleting some (can be none) of the characters without disturbing the relative positions of the remaining characters. (ie, [2,3,5] is a subsequence of [1,2,3,4,5] while [1,5,3] is not).

# Solution, O(n^2) time and space
# It is important we multiply numbers together, to ensure the amount of numbers we pick from each list is the same. Our dp state is [i:] and [j:] for the remaining arrays. We can either multiply the first two together, or ignore one of the numbers. I also just added a state to ensure we have taken a number, though there are probably better ways to handle this. I realized when coding I didn't really consider the case of [a, b] [c, d] where optimal is a*d + b*c, but this goes against the definition of the dot product.

class Solution:
    def maxDotProduct(self, nums1: List[int], nums2: List[int]) -> int:
        # solves the subproblem for [i:] in nums1 and [j:] in nums2
        @cache
        def dp(i, j, isNumTaken):
            # base case
            if i == len(nums1) or j == len(nums2):
                if isNumTaken:
                    return 0
                return float('-inf')

            resForThis = float('-inf')

            # if we multiple the two numbers together
            ifMultFirstTwo = nums1[i] * nums2[j] + dp(i + 1, j + 1, True)

            # if we consider delaying
            ifDelayNums2 = dp(i, j + 1, isNumTaken)

            ifDelayNums1 = dp(i + 1, j, isNumTaken)

            resForThis = max(ifMultFirstTwo, ifDelayNums2, ifDelayNums1)

            return resForThis

        return dp(0, 0, False)
