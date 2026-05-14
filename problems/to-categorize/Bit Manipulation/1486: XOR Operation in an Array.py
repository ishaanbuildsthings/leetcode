# https://leetcode.com/problems/xor-operation-in-an-array/description/
# difficulty: easy
# tags: bit manipulation

# Problem
# You are given an integer n and an integer start.

# Define an array nums where nums[i] = start + 2 * i (0-indexed) and n == nums.length.

# Return the bitwise XOR of all elements of nums.

# Solution, O(n) time and space
# I couldn't think of a closed form solution so I simulated

class Solution:
    def xorOperation(self, n: int, start: int) -> int:
        res = 0
        for i in range(n):
            num = start + (2 * i)
            res = res ^ num
        return res