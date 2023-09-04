# https://leetcode.com/problems/maximum-size-subarray-sum-equals-k/
# Difficulty: Medium
# Tags: prefix

# Problem
# Given an integer array nums and an integer k, return the maximum length of a subarray that sums to k. If there is not one, return 0 instead.

# Solution, O(n) time, O(n) space
# Iterate through, tracking the sum. Track the earliest occurence of each prefix sum. For each index, figure out the difference we need to cut off to reach the target, and update the result.

class Solution:
    def maxSubArrayLen(self, nums: List[int], k: int) -> int:
        prefix = {} # maps a prefix sum to the earliest index it occured at
        prefix[0] = -1 # we can always cut off nothing and lose a sum of 0

        result = 0
        running_sum = 0
        for i, num in enumerate(nums):
            running_sum += num
            if running_sum not in prefix:
                prefix[running_sum] = i
            lop_off = running_sum - k
            if lop_off in prefix:
                length = i - prefix[lop_off]
                result = max(result, length)

        return result
