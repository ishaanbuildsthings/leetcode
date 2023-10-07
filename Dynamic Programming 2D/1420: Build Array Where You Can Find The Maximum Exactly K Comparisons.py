# https://leetcode.com/problems/build-array-where-you-can-find-the-maximum-exactly-k-comparisons/description/
# difficulty: hard
# tags: dynamic programming 2d, digit dp

# problem
# You are given three integers n, m and k. Consider the following algorithm to find the maximum element of an array of positive integers:


# You should build the array arr which has the following properties:

# arr has exactly n integers.
# 1 <= arr[i] <= m where (0 <= i < n).
# After applying the mentioned algorithm to arr, the value search_cost is equal to k.
# Return the number of ways to build the array arr under the mentioned conditions. As the answer may grow large, the answer must be computed modulo 109 + 7.

# Solution, O(n * k * m^2) time, O(n*k*m) space
# Standard digit dp style solution, add digits based on valid ranges and add to the result if we have a valid base case

MOD = 10**9 + 7

class Solution:
    def numOfArrays(self, n: int, m: int, k: int) -> int:
        @cache
        def dp(prevMax, i, currentCost):
            # base case
            if i == n:
                return 1 if currentCost == k else 0

            resForThis = 0
            # we can take numbers below the previous max, and gain no search cost
            for nextNum in range(1, prevMax + 1):
                resForThis += dp(prevMax, i + 1, currentCost)

            # we can take numbers above the previous max and gain a search cost
            if currentCost < k: # pruning, can add even more if we don't have enough higher numbers to reach k given the amount of numbers we can still add
                for nextNum in range(prevMax + 1, m + 1):
                    resForThis += dp(nextNum, i + 1, currentCost + 1)

            return resForThis % MOD

        return dp(0, 0, 0)
