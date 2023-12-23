# https://leetcode.com/problems/range-sum-of-sorted-subarray-sums/description/
# difficulty: medium

# problem
# You are given the array nums consisting of n positive integers. You computed the sum of all non-empty continuous subarrays from the array and then sorted them in non-decreasing order, creating a new array of n * (n + 1) / 2 numbers.

# Return the sum of the numbers from index left to index right (indexed from 1), inclusive, in the new array. Since the answer can be a huge number return it modulo 109 + 7.

# Solution, n^2 log n time, n^2 space
# I got every array sum then sorted them. This is a brute force solution and there is definitely better.

class Solution:
    def rangeSum(self, nums: List[int], n: int, left: int, right: int) -> int:
        arraySums = []
        for l in range(len(nums)):
            runningSum = 0
            for r in range(l, len(nums)):
                runningSum += nums[r]
                arraySums.append(runningSum)
        arraySums.sort()
        return sum(arraySums[left - 1:right]) % (10**9 + 7)
