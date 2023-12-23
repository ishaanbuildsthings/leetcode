# https://leetcode.com/problems/neither-minimum-nor-maximum/
# Difficulty: Easy

# Problem
# Given an integer array nums containing distinct positive integers, find and return any number from the array that is neither the minimum nor the maximum value in the array, or -1 if there is no such number.

# Return the selected integer.

# Solution, O(1) time and space, pick the middle of the smallest 3 elements

class Solution:
    def findNonMinOrMax(self, nums: List[int]) -> int:
        if len(nums) <= 2:
            return -1
        three = nums[0:3]
        three.sort() # this could be linear time instead of 3 log 3
        return three[1]