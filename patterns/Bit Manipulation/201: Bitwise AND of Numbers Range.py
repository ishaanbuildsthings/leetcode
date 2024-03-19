# https://leetcode.com/problems/bitwise-and-of-numbers-range/?envType=daily-question&envId=2024-02-21
# difficulty: medium
# tags: bit manipulation

# Problem
# Given two integers left and right that represent the range [left, right], return the bitwise AND of all numbers in this range, inclusive.

# Solution, O(n) time O(1) space, bit math
class Solution:
    def rangeBitwiseAnd(self, left: int, right: int) -> int:
        res = 0
        top = math.ceil(math.log2(right)) + 1 if right != 0 else 1
        for bit in range(top):
            if left >> bit & 1 and right - left <= 2**bit and right >> bit & 1:
                res |= 2**bit
        return res

        # 111
        # ^
        # 421



        # 1 (2) 3 (4) 5 (6) 7 (8) 9


        # 4  5  6 7 (8 9 10 11)     12 13 14 15 (16)

        # 1 2 (3 4) 5 6 (7 8)