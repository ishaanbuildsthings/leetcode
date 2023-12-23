# https://leetcode.com/problems/combination-sum-iv/description/?envType=daily-question&envId=2023-09-09
# Difficulty: Medium
# Tags: Dynamic Programming 1d

# Problem
# Given an array of distinct integers nums and a target integer target, return the number of possible combinations that add up to target.

# The test cases are generated so that the answer can fit in a 32-bit integer.

# Solution, O(n * target) time, O(target) space
# Create a dp of size target. For each dp state, try taking every number.

class Solution:
    def combinationSum4(self, nums: List[int], target: int) -> int:
        # memo[target] tells us the answer to that subproblem

        memo = [-1 for _ in range(target + 1)]

        def dp(t):
            # base case
            if t == 0:
                return 1

            if memo[t] != -1:
                return memo[t]

            # for a given target remaining, we can try taking all possible numbers once and reducing the problem
            res_for_this = 0
            for num in nums:
                if num > t:
                    continue
                res_for_this += dp(t - num)

            memo[t] = res_for_this
            return res_for_this

        return dp(target)

