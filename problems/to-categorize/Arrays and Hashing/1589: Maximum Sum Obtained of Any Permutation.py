# https://leetcode.com/problems/maximum-sum-obtained-of-any-permutation/
# difficulty: medium
# tags: sweep line

# problem
# We have an array of integers, nums, and an array of requests where requests[i] = [starti, endi]. The ith request asks for the sum of nums[starti] + nums[starti + 1] + ... + nums[endi - 1] + nums[endi]. Both starti and endi are 0-indexed.

# Return the maximum total sum of all requests among all permutations of nums.

# Since the answer may be too large, return it modulo 109 + 7.

# Solution, O(n log n) time, O(n) space
# Get the number of times each element is requested. Then in order of the most requested ones, we assume we use the biggest number.

class Solution:
    def maxSumRangeQuery(self, nums: List[int], requests: List[List[int]]) -> int:
        sweep = [0 for _ in range(len(nums) + 1)] # help record how many times a cell is requested
        for l, r in requests:
            sweep[l] += 1
            sweep[r + 1] -= 1

        runningCount = 0
        for i in range(len(sweep)):
            runningCount += sweep[i]
            sweep[i] = runningCount
        sweep.pop()
        nums.sort(reverse=True)
        sweep.sort(reverse=True)
        res = 0
        for i in range(len(sweep)):
            res += nums[i] * sweep[i]
            res = res % (10**9 + 7)
        return res



