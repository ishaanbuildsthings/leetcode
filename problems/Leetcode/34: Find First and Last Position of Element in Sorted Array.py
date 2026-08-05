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




# // https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/description/
# // Difficulty: Medium
# // Tags: Binary Search

# // Problem
# /*
# Given an array of integers nums sorted in non-decreasing order, find the starting and ending position of a given target value.

# If target is not found in the array, return [-1, -1].

# You must write an algorithm with O(log n) runtime complexity.
# Input: nums = [5,7,7,8,8,10], target = 8
# Output: [3,4]
# */

# // Solution: O(log n^2) time, which is O(log n), and O(1) space. Do a binary search to locate the first position of the target, and do a second to locate the last.

# var searchRange = function (nums, target) {
#   let l = 0;
#   let r = nums.length - 1;
#   let m = Math.floor((r + l) / 2);

#   // look for the first index of our target
#   while (l < r) {
#     m = Math.floor((r + l) / 2);
#     const num = nums[m];

#     // if we see our exact target, we can try to find a further left target, but it isn't guaranteed
#     if (num === target) {
#       r = m;
#     }
#     // if our number is too small, consider numbers strictly to the right
#     else if (num < target) {
#       l = m + 1;
#     }
#     // if our number is too large, we can consider numbers strictly to the left
#     else if (num > target) {
#       r = m - 1;
#     }
#   }

#   if (nums[l] !== target) {
#     return [-1, -1];
#   }

#   const leftIndex = l;

#   l = 0;
#   r = nums.length - 1;
#   m = Math.floor((r + l) / 2);

#   // look for the last index of our target

#   while (l < r) {
#     m = Math.ceil((r + l) / 2);
#     const num = nums[m];

#     // if we see our exact target, we can try looking right, but need to include our number still
#     if (num === target) {
#       l = m;
#     }
#     // if our number is smaller than the target, we need to look strictly to the right
#     if (num < target) {
#       l = m + 1;
#     }
#     // if our number is bigger than the target, we need to look strictly left
#     else if (num > target) {
#       r = m - 1;
#     }
#   }

#   return [leftIndex, l];
# };
