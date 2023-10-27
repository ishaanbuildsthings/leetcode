# https://leetcode.com/problems/matrix-diagonal-sum/description/
# difficulty: easy

# Problem
# Given a square matrix mat, return the sum of the matrix diagonals.

# Only include the sum of all the elements on the primary diagonal and all the elements on the secondary diagonal that are not part of the primary diagonal.

# Solution, O(diagonal) time, O(1) space

class Solution:
    def diagonalSum(self, mat: List[List[int]]) -> int:
        res = 0
        for primary in range(len(mat)):
            print(primary)
            res += mat[primary][primary]
            res += mat[primary][len(mat) - primary - 1]
        if len(mat) % 2 == 1:
            mid = len(mat) // 2
            return res - mat[mid][mid]
        return res

