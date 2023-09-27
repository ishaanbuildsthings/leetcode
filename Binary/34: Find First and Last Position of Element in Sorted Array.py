# https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/description/
# difficulty: medium
# tags: binary search

# problem
# Given an array of integers nums sorted in non-decreasing order, find the starting and ending position of a given target value.

# If target is not found in the array, return [-1, -1].

# You must write an algorithm with O(log n) runtime complexity.

# Solution, O(log n) time, O(1) space, just binary search for first and last
class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        # edge case
        if not nums:
            return [-1, -1]
        print(nums)
        print(target)
        l = 0
        r = len(nums) - 1
        # find first position
        while l < r:
            m = (r + l) // 2 # m is the index we check
            if nums[m] < target:
                l = m + 1
            else:
                r = m
        if nums[r] != target:
            return [-1, -1]
        firstPos = r
        # find the second position
        l = firstPos
        r = len(nums) - 1
        while l < r:
            m = math.ceil((r + l) / 2)
            if nums[m] <= target:
                l = m
            else:
                r = m - 1
        return [firstPos, r]

