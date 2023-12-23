# https://leetcode.com/problems/richest-customer-wealth/
# Difficulty: Easy

# Problem
# You are given an m x n integer grid accounts where accounts[i][j] is the amount of money the i​​​​​​​​​​​th​​​​ customer has in the j​​​​​​​​​​​th​​​​ bank. Return the wealth that the richest customer has.

# A customer's wealth is the amount of money they have in all their bank accounts. The richest customer is the customer that has the maximum wealth.

# Solution, O(m*n) time, O(1) space
# Just iterate and count each row

class Solution:
    def maximumWealth(self, accounts: List[List[int]]) -> int:
        res = 0
        for vault in accounts:
            res = max(res, sum(vault))
        return res

