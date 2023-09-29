# https://leetcode.com/problems/monotonic-array/description/?envType=daily-question&envId=2023-09-29
# difficulty: easy

# problem
# An array is monotonic if it is either monotone increasing or monotone decreasing.

# An array nums is monotone increasing if for all i <= j, nums[i] <= nums[j]. An array nums is monotone decreasing if for all i <= j, nums[i] >= nums[j].

# Given an integer array nums, return true if the given array is monotonic, or false otherwise.

# Solution, O(n) time and O(1) space, track the direction if we move that way

class Solution:
    def isMonotonic(self, nums: List[int]) -> bool:
        dir = 'neutral'
        for i, num in enumerate(nums):
            if i == 0:
                continue
            if nums[i] == nums[i - 1]:
                continue
            if nums[i] > nums[i - 1]:
                if dir == 'down':
                    return False
                if dir == 'neutral':
                    dir = 'up'
            elif nums[i] < nums[i - 1]:
                if dir == 'up':
                    return False
                if dir == 'neutral':
                    dir = 'down'

        return True
