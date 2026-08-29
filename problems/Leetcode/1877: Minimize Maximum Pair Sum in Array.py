# https://leetcode.com/problems/minimize-maximum-pair-sum-in-array/description/
# difficulty: medium

# problem
# The pair sum of a pair (a,b) is equal to a + b. The maximum pair sum is the largest pair sum in a list of pairs.

# For example, if we have pairs (1,5), (2,3), and (4,4), the maximum pair sum would be max(1+5, 2+3, 4+4) = max(6, 5, 8) = 8.
# Given an array nums of even length n, pair up the elements of nums into n / 2 pairs such that:

# Each element of nums is in exactly one pair, and
# The maximum pair sum is minimized.
# Return the minimized maximum pair sum after optimally pairing up the elements.

# Solution, O(n log n) time, O(sort) space
# Just pair the biggest element with the smallest and so on

class Solution:
    def minPairSum(self, nums: List[int]) -> int:
        nums.sort()
        smallestMax = float('-inf')
        for i in range(int(len(nums) / 2)):
            smallestMax = max(smallestMax, nums[i] + nums[len(nums) - i - 1])
        return smallestMax