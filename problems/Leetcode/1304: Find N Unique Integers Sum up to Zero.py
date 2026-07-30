# https://leetcode.com/problems/find-n-unique-integers-sum-up-to-zero/
# difficulty: easy

# Problem
# Given an integer n, return any array containing n unique integers such that they add up to 0.

# Solution, O(n) time and O(1) space

class Solution:
    def sumZero(self, n: int) -> List[int]:
        res = []
        total = 0
        for i in range(1, n):
            res.append(i)
            total += i
        res.append(0 - total)
        return res
