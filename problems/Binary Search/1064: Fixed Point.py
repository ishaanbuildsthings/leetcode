# https://leetcode.com/problems/fixed-point/description/
# difficulty: easy
# tags: binary search

# Problem
# Given an array of distinct integers arr, where arr is sorted in ascending order, return the smallest index i that satisfies arr[i] == i. If there is no such index, return -1.

# Solution, O(log n) time, O(1) space

class Solution:
    def fixedPoint(self, arr: List[int]) -> int:
        l = 0
        r = len(arr) - 1
        while l <= r:
            m = (r + l) // 2
            num = arr[m]
            if num >= m:
                r = m - 1
            else:
                l = m + 1
        if r + 1 == len(arr):
            return -1
        return r + 1 if arr[r + 1] == r + 1 else -1

