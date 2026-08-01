# https://leetcode.com/problems/special-positions-in-a-binary-matrix/description/?envType=daily-question&envId=2023-12-13
# difficulty: easy

# Problem
# Given an m x n binary matrix mat, return the number of special positions in mat.

# A position (i, j) is called special if mat[i][j] == 1 and all other elements in row i and column j are 0 (rows and columns are 0-indexed).

# Solution, lots of ways to solve, O(1) space, 1-pass, only check certain rows/columns, etc. I did an O(m*n) time and O(width) space solution.

class Solution:
    def numSpecial(self, mat: List[List[int]]) -> int:
        height = len(mat)
        width = len(mat[0])

        colSums = {
            c : sum(mat[r][c] for r in range(height))
            for c in range(width)
        }

        res = 0
        for r in range(height):
            seenPos = None
            for c in range(width):
                if mat[r][c]:
                    if seenPos != None:
                        seenPos = None
                        break
                    seenPos = c
            if seenPos != None and colSums[seenPos] == 1:
                res += 1
        return res