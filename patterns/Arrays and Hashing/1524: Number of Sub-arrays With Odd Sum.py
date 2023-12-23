# https://leetcode.com/problems/number-of-sub-arrays-with-odd-sum/
# difficulty: medium
# tags: lop off

# Problem
# Given an array of integers arr, return the number of subarrays with an odd sum.

# Since the answer can be very large, return it modulo 109 + 7.

# Solution, O(n) time and O(1) space, track odd an evens using lop off method

class Solution:
    def numOfSubarrays(self, arr: List[int]) -> int:
        oddCounts = 0
        evenCounts = 1 # can always cut off nothing
        runningSum = 0
        res = 0
        for num in arr:
            runningSum += num
            if runningSum % 2 == 0:
                res += oddCounts
                evenCounts += 1
            else:
                res += evenCounts
                oddCounts += 1
        return res % (10**9 + 7)