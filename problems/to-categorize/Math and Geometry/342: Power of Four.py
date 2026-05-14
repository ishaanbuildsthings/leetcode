# https://leetcode.com/problems/power-of-four/description/
# difficulty: easy
# tags: math

# problem
# Given an integer n, return true if it is a power of four. Otherwise, return false.

# An integer n is a power of four, if there exists an integer x such that n == 4x.

# Solution, O(1) time and space, or O(log n) time if you want. Could also just store all powers of 4.

class Solution:
    def isPowerOfFour(self, n: int) -> bool:
        # edge cases
        if n <= 0:
            return False
        return (math.log(n) / math.log(4)) == math.floor((math.log(n) / math.log(4)))