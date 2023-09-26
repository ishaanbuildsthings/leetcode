# https://leetcode.com/problems/three-consecutive-odds/description/
# difficulty: easy

# problem
# Given an integer array arr, return true if there are three consecutive odd numbers in the array. Otherwise, return false.

# Solution, O(n) time and O(1) space
class Solution:
    def threeConsecutiveOdds(self, arr: List[int]) -> bool:
        for i in range(len(arr) - 2):
            if arr[i]*arr[i+1]*arr[i+2] % 2 == 1: # don't want to type each mod
                return True
        return False