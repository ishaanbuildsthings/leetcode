# https://leetcode.com/problems/largest-submatrix-with-rearrangements/description/?envType=daily-question&envId=2023-11-26
# difficulty: medium
# tags: stack

# Problem
# You are given a binary matrix matrix of size m x n, and you are allowed to rearrange the columns of the matrix in any order.

# Return the area of the largest submatrix within matrix where every element of the submatrix is 1 after reordering the columns optimally.

# Solution
# We can make a matrix where each cell is the contiguous amount of 1s above it. Now, for each row, we sort that row and scan over finding the largest rectangle, assuming we have a base at the row we scan from.

class Solution:
    def largestSubmatrix(self, matrix: List[List[int]]) -> int:
        height = len(matrix)
        width = len(matrix[0])

        heightMatrix = [row[:] for row in matrix]
        for c in range(width):
            streak = 0
            for r in range(height):
                if heightMatrix[r][c] == 0:
                    streak = 0
                else:
                    streak += 1
                heightMatrix[r][c] = streak

        res = 0

        for row in heightMatrix:
            row.sort()
            for i in range(len(row)):
                width = len(row) - i
                height = row[i]
                res = max(res, width * height)

        return res


