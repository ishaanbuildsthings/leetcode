# https://leetcode.com/problems/sort-colors/description/
# difficulty: medium
# tags: bucket sort

# Problem
# Given an array nums with n objects colored red, white, or blue, sort them in-place so that objects of the same color are adjacent, with the colors in the order red, white, and blue.

# We will use the integers 0, 1, and 2 to represent the color red, white, and blue, respectively.

# You must solve this problem without using the library's sort function.

# Solution, O(n) time and O(1) space, standard bucket sort

class Solution:
    def sortColors(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        counts = Counter(nums)
        c_i = 0
        for i in range(len(nums)):
            while not counts[c_i]:
                c_i += 1
            nums[i] = c_i
            counts[c_i] -= 1

