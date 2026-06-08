# https://leetcode.com/problems/minimum-flips-to-make-a-or-b-equal-to-c/description/
# difficulty: medium
# tags: bit manipulation

# Problem
# Given 3 positives numbers a, b and c. Return the minimum flips required in some bits of a and b to make ( a OR b == c ). (bitwise OR operation).
# Flip operation consists of change any single bit 1 to 0 or change the bit 0 to 1 in their binary representation.

# Solution, O(1) time and space, check each bit

MAX_BITS = math.ceil(math.log2(10**9))
class Solution:
    def minFlips(self, a: int, b: int, c: int) -> int:
        res = 0
        for offset in range(MAX_BITS - 1, -1, -1):
            aBit = (a >> offset) & 1
            bBit = (b >> offset) & 1
            cBit = (c >> offset) & 1
            if not cBit:
                res += aBit + bBit
            else:
                res += 1 if not (aBit or bBit) else 0
        return res