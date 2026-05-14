# https://leetcode.com/problems/count-strictly-increasing-subarrays/description/
# Difficulty: Medium
# Tags: prefix

# Problem
# You are given an array nums consisting of positive integers.

# Return the number of subarrays of nums that are in strictly increasing order.

# A subarray is a contiguous part of an array.

# Solution, O(n) time, O(1) space
# Iterate, tracking the previous largest number (honestly we can just look at the previous number). If we are bigger, we add the tracked length of the subarray to the result, otherwise reset.

class Solution:
    def countSubarrays(self, nums: List[int]) -> int:
        result = 0
        current_length = 0
        prev_max = 0
        for num in nums:
            if num > prev_max:
                prev_max = num
                current_length += 1
            else:
                prev_max = num
                current_length = 1
            result += current_length
        return result
