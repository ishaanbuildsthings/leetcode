# https://leetcode.com/problems/final-value-of-variable-after-performing-operations/
# difficulty: easy

# problem
# There is a programming language with only four operations and one variable X:

# ++X and X++ increments the value of the variable X by 1.
# --X and X-- decrements the value of the variable X by 1.
# Initially, the value of X is 0.

# Given an array of strings operations containing a list of operations, return the final value of X after performing all the operations.

# Solution, O(n) time, O(1) space, check each operation

class Solution:
    def finalValueAfterOperations(self, operations: List[str]) -> int:
        res = 0
        for op in operations:
            if '+' in op:
                res += 1
            else:
                res -= 1
        return res