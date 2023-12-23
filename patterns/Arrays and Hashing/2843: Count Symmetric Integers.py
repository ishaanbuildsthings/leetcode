# https://leetcode.com/problems/count-symmetric-integers/
# difficulty: easy

# problem
# You are given two positive integers low and high.

# An integer x consisting of 2 * n digits is symmetric if the sum of the first n digits of x is equal to the sum of the last n digits of x. Numbers with an odd number of digits are never symmetric.

# Return the number of symmetric integers in the range [low, high].

# Solution, O(range) time, O(1) space

class Solution:
    def countSymmetricIntegers(self, low: int, high: int) -> int:
        res = 0
        for num in range(low, high + 1):
            numStr = str(num)
            if len(numStr) % 2 == 1:
                continue
            leftSum = 0
            for i in range(int(len(numStr) / 2)):
                leftSum += int(numStr[i])
            rightSum = 0
            for i in range(int(len(numStr) / 2), len(numStr)):
                rightSum += int(numStr[i])
            if leftSum == rightSum:
                res += 1
        return res