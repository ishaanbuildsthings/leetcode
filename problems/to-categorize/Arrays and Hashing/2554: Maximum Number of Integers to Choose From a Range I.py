# https://leetcode.com/problems/maximum-number-of-integers-to-choose-from-a-range-i/description/
# difficulty: medium

# Problem
# You are given an integer array banned and two integers n and maxSum. You are choosing some number of integers following the below rules:

# The chosen integers have to be in the range [1, n].
# Each integer can be chosen at most once.
# The chosen integers should not be in the array banned.
# The sum of the chosen integers should not exceed maxSum.
# Return the maximum number of integers you can choose following the mentioned rules.

# Solution, keep adding up to n numbers, terminate if the sum becomes too big. There are other solutions too in the solutions tab.

class Solution:
    def maxCount(self, banned: List[int], n: int, maxSum: int) -> int:
        bannedSet = set(banned)
        currSum = 0
        res = 0
        for num in range(1, n + 1):
            if num in bannedSet:
                continue
            currSum += num
            res += 1
            if currSum > maxSum:
                return res - 1
        return res