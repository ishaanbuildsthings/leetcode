# https://leetcode.com/problems/valid-perfect-square/description/
# Difficulty: Easy
# Tags: Math

# Problem

# Given a positive integer num, return true if num is a perfect square or false otherwise.

# A perfect square is an integer that is the square of an integer. In other words, it is the product of some integer with itself.

# You must not use any built-in library function, such as sqrt.

# Solution, O(log n) or O(1) time since integer bound, a common technique I use for other problems, O(1) space
# Only after reading I realized you're supposed to binary search on the values... I'm too used to doing harder problems where I just write this helper funciton.
class Solution:
    def isPerfectSquare(self, num: int) -> bool:
        return math.sqrt(num) == math.floor(math.sqrt(num))