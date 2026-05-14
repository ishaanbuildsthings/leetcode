# https://leetcode.com/problems/find-in-mountain-array/?envType=daily-question&envId=2023-10-12
# difficulty: hard
# tags: binary search

# Problem
# (This problem is an interactive problem.)

# You may recall that an array arr is a mountain array if and only if:

# arr.length >= 3
# There exists some i with 0 < i < arr.length - 1 such that:
# arr[0] < arr[1] < ... < arr[i - 1] < arr[i]
# arr[i] > arr[i + 1] > ... > arr[arr.length - 1]
# Given a mountain array mountainArr, return the minimum index such that mountainArr.get(index) == target. If such an index does not exist, return -1.

# You cannot access the mountain array directly. You may only access the array using a MountainArray interface:

# MountainArray.get(k) returns the element of the array at index k (0-indexed).
# MountainArray.length() returns the length of the array.
# Submissions making more than 100 calls to MountainArray.get will be judged Wrong Answer. Also, any solutions that attempt to circumvent the judge will result in disqualification.

# Solution, O(log n) time, O(1) space
# Binary search once to find the peak, then again on the left for the target, then again on the right for the target. I believe there's faster than 3 binary searches (I thought of one with two before, I think). There's also many optimizations in this problem I didn't include (early termination if we find the peak, changing boundaries of future searches, etc)

# """
# This is MountainArray's API interface.
# You should not implement it, or speculate about its implementation
# """
#class MountainArray:
#    def get(self, index: int) -> int:
#    def length(self) -> int:

class Solution:
    def findInMountainArray(self, target: int, mountain_arr: 'MountainArray') -> int:
        n = mountain_arr.length()
        # find peak
        l = 1
        r = n - 2
        while l <= r:
            m = (r + l) // 2
            left = mountain_arr.get(m - 1)
            middle = mountain_arr.get(m)
            right = mountain_arr.get(m + 1)
            # if we found the peak
            if left < middle and middle > right:
                l = m
                r = m
                break
            # if the peak is to the right
            elif left < middle:
                l = m + 1
            else:
                r = m - 1
        peakIndex = l
        # find the first occurence in the left
        l = 0
        r = peakIndex
        while l <= r:
            m = (r + l) // 2
            middle = mountain_arr.get(m)
            if middle == target:
                return m
            elif middle > target:
                r = m - 1
            else:
                l = m + 1

        # find the first occurence in the right
        l = peakIndex
        r = n - 1
        while l <= r:
            m = (r + l) // 2
            middle = mountain_arr.get(m)
            if middle == target:
                return m
            elif middle > target:
                l = m + 1
            else:
                r = m - 1

        return -1





