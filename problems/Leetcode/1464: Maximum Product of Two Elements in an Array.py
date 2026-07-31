# https://leetcode.com/problems/maximum-product-of-two-elements-in-an-array/description/?envType=daily-question&envId=2023-12-12
# difficulty: easy

# Problem
# Given the array of integers nums, you will choose two different indices i and j of that array. Return the maximum value of (nums[i]-1)*(nums[j]-1).

# Solution, O(n) time O(1) space, find the biggest two, bubble sort esque

class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        m1 = m2 = float('-inf')
        for num in nums:
            if num > m1:
                m1 = num
            if m1 > m2:
                m1, m2 = m2, m1
        return (m1 - 1) * (m2 - 1)
