# https://leetcode.com/problems/transpose-matrix/description/?envType=daily-question&envId=2023-12-10
# difficulty: easy
# tags: functional

# Problem
# Given a 2D integer array matrix, return the transpose of matrix.

# The transpose of a matrix is the matrix flipped over its main diagonal, switching the matrix's row and column indices.

# Solution, O(n*m) time, O(1) space

class Solution:
    def transpose(self, matrix: List[List[int]]) -> List[List[int]]:
        return [ [matrix[c][r] for c in range(len(matrix))] for r in range(len(matrix[0])) ]