# https://leetcode.com/problems/check-if-every-row-and-column-contains-all-numbers/
# difficulty: easy

# Problem
# An n x n matrix is valid if every row and every column contains all the integers from 1 to n (inclusive).

# Given an n x n integer matrix matrix, return true if the matrix is valid. Otherwise, return false.

# Solution, O(n^2) time, O(n) space, valid each row and column one at a time. We can use O(1) space by marking the numbers as negative when we have seen them, then fixing them.

class Solution:
    def checkValid(self, matrix: List[List[int]]) -> bool:
        for row in matrix:
            seen = set()
            for num in row:
                if num in seen or num < 1 or num > len(matrix):
                    return False
                seen.add(num)
        for c in range(len(matrix)):
            seen = set()
            for r in range(len(matrix)):
                num = matrix[r][c]
                if num in seen or num < 1 or num > len(matrix):
                    return False
                seen.add(num)

        return True