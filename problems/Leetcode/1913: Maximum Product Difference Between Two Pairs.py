# https://leetcode.com/problems/maximum-product-difference-between-two-pairs/description/?envType=daily-question&envId=2023-12-18
# difficulty: easy

# Problem
# The product difference between two pairs (a, b) and (c, d) is defined as (a * b) - (c * d).

# For example, the product difference between (5, 6) and (2, 7) is (5 * 6) - (2 * 7) = 16.
# Given an integer array nums, choose four distinct indices w, x, y, and z such that the product difference between pairs (nums[w], nums[x]) and (nums[y], nums[z]) is maximized.

# Return the maximum such product difference.

# Solution, O(n) time O(1) space, get the two biggest and two smallest and get the difference.

class Solution:
    def maxProductDifference(self, nums: List[int]) -> int:
        max1 = max2 = 0
        min1 = min2 = float('inf')
        for num in nums:
            max1 = max(max1, num)
            if max1 > max2:
                max1, max2 = max2, max1
            min1 = min(min1, num)
            if min1 < min2:
                min1, min2 = min2, min1
        return (max1 * max2) - (min1 * min2)

