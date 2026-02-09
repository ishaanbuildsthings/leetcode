# https://leetcode.com/problems/maximum-average-subarray-i/description/
# difficulty: easy
# tags: sliding window fixed

# Problem
# You are given an integer array nums consisting of n elements, and an integer k.

# Find a contiguous subarray whose length is equal to k that has the maximum average value and return this value. Any answer with a calculation error less than 10-5 will be accepted.

# Solution, O(n) time and O(1) space, standard fixed window

class Solution:
    def findMaxAverage(self, nums: List[int], k: int) -> float:
        l = 0
        r = 0
        total = 0
        while r < k:
            newNum = nums[r]
            total += newNum
            r += 1

        res = total / k
        while r < len(nums):
            newNum = nums[r]
            total += newNum
            lostNum = nums[l]
            total -= lostNum
            newAvg = total / k
            res = max(res, newAvg)
            r += 1
            l += 1

        return res