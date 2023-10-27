# https://leetcode.com/problems/closest-divisors/
# Difficulty: medium
# tags: math

# Problem
# Given an integer num, find the closest two integers in absolute difference whose product equals num + 1 or num + 2.

# Return the two integers in any order.

# Solution, O(root(n)) time, O(1) space
# Just check both options and iterate up to root n factors

class Solution:
    def closestDivisors(self, num: int) -> List[int]:
        maxDiff = float('inf')
        res = [None, None]

        def getPairs(n):
            nonlocal maxDiff, res
            for firstDivisor in range(1, math.floor(math.sqrt(n)) + 1):
                second = n / firstDivisor
                if int(second) != second:
                    continue
                diff = abs(firstDivisor - second)
                if diff < maxDiff:
                    maxDiff = diff
                    res = [int(firstDivisor), int(second)]

        getPairs(num + 1)
        getPairs(num + 2)

        return res
