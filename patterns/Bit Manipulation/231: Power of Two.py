# https://leetcode.com/problems/power-of-two/description/
# difficulty: easy
# tags: bit manipulation

# Problem
# Given an integer n, return true if it is a power of two. Otherwise, return false.

# An integer n is a power of two, if there exists an integer x such that n == 2x.

# Solution, O(log n or constant) time, O(1) space, I just counted if there is a single one bit, there's other solutuions like n & -n == n, or n & (n - 1) == 0

class Solution:
    def isPowerOfTwo(self, n: int) -> bool:
        oneBits = 0
        for offset in range(33):
            bit = (n >> offset) & 1
            oneBits += bit
            if oneBits > 1:
                return False
        return oneBits == 1