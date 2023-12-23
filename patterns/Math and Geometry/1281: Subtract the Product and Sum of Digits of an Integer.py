# https://leetcode.com/problems/subtract-the-product-and-sum-of-digits-of-an-integer/description/
# difficulty: easy
# tags: math

# problem
# Given an integer number n, return the difference between the product of its digits and the sum of its digits.

# Solution, O(log n) time, O(1) space

class Solution:
    def subtractProductAndSum(self, n: int) -> int:
        digitSum = 0
        product = 1
        while n > 0:
            lastDigit = n % 10
            digitSum += lastDigit
            product *= lastDigit
            n //= 10
        return product - digitSum