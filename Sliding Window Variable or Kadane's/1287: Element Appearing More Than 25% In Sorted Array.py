# https://leetcode.com/problems/element-appearing-more-than-25-in-sorted-array/description/?envType=daily-question&envId=2023-12-11
# difficulty: easy
# tags: sliding window variable

# Problem
# Given an integer array sorted in non-decreasing order, there is exactly one integer in the array that occurs more than 25% of the time, return that integer.

# Solution, O(n) time and O(1) space, sliding window. We can also just check for every index if the 25%th to the right is the same number.

class Solution:
    def findSpecialInteger(self, arr: List[int]) -> int:
        l = 0
        r = 0

        while r < len(arr):
            while arr[l] != arr[r]:
                l += 1
            if (r - l + 1) > 0.25 * len(arr):
                return arr[r]
            r += 1

