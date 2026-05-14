# https://leetcode.com/problems/minimize-product-sum-of-two-arrays/
# difficulty: medium
# tags: greedy

# problem
# The product sum of two equal-length arrays a and b is equal to the sum of a[i] * b[i] for all 0 <= i < a.length (0-indexed).

# For example, if a = [1,2,3,4] and b = [5,2,3,1], the product sum would be 1*5 + 2*2 + 3*3 + 4*1 = 22.
# Given two arrays nums1 and nums2 of length n, return the minimum product sum if you are allowed to rearrange the order of the elements in nums1.

# Solution, O(n log n) time, O(sort) space
# Just sort the two arrays backwards to each other and multiply to get minimum efficiency.

class Solution:
    def minProductSum(self, nums1: List[int], nums2: List[int]) -> int:
        nums1.sort()
        nums2.sort(reverse=True)
        res = 0
        for i in range(len(nums1)):
            res += nums1[i] * nums2[i]
        return res