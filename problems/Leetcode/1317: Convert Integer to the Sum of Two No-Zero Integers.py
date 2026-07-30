# https://leetcode.com/problems/convert-integer-to-the-sum-of-two-no-zero-integers/
# difficulty: easy
# tags: math

# Problem
# No-Zero integer is a positive integer that does not contain any 0 in its decimal representation.

# Given an integer n, return a list of two integers [a, b] where:

# a and b are No-Zero integers.
# a + b = n
# The test cases are generated so that there is at least one valid solution. If there are many valid solutions, you can return any of them.

# Solution, O(n * log n) time, O(1) space

class Solution:
    def getNoZeroIntegers(self, n: int) -> List[int]:
        def hasZero(num):
            while num:
                lastDigit = num % 10
                if not lastDigit:
                    return True
                num //= 10
            return False

        for firstNum in range(1, n):
            secondNum = n - firstNum
            if not hasZero(firstNum) and not hasZero(secondNum):
                return [firstNum, secondNum]
