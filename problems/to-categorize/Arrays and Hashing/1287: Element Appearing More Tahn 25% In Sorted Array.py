# https://leetcode.com/problems/element-appearing-more-than-25-in-sorted-array/description/
# difficulty: easy
# tags: binary search, sliding window variable

# Problem
# Given an integer array sorted in non-decreasing order, there is exactly one integer in the array that occurs more than 25% of the time, return that integer.

# Solution, I wrote a basic sliding window. But for each index we can just look 25% ahead and see if it matches. There's also an even better binary search solution.

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

