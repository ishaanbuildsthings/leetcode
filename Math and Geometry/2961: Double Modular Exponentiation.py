# https://leetcode.com/problems/double-modular-exponentiation/description/
# difficulty: medium
# tags: math, contest

# Problem
# You are given a 0-indexed 2D array variables where variables[i] = [ai, bi, ci, mi], and an integer target.

# An index i is good if the following formula holds:

# 0 <= i < variables.length
# ((aibi % 10)ci) % mi == target
# Return an array consisting of good indices in any order.


# Solution, O(queries * (logB + logC)) time, O(max(logB, logC)) space


class Solution:
    def getGoodIndices(self, variables: List[List[int]], target: int) -> List[int]:

        @cache
        def modPow(base, exponent, mod):
            if exponent == 0:
                return 1
            if exponent == 1:
                return base % mod
            half = modPow(base, exponent // 2, mod)
            if exponent % 2 == 0:
                return (half * half) % mod
            else:
                return (half * half * base) % mod



        res = []
        for i in range(len(variables)):
            start = modPow(variables[i][0], variables[i][1], 10)
            start = modPow(start, variables[i][2], variables[i][3])
            if start == target:
                res.append(i)
        return res