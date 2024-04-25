# https://leetcode.com/problems/count-submatrices-with-top-left-element-and-sum-less-than-k/description/
# difficulty: medium
# tags: prefix, range query

# Solution, O(n*m) time and space, can do with just a column prefix array API

class RangeSumQuery2d:
    def __init__(self, matrix):
        self.matrix = matrix
        self.prefixSums = [[0 for _ in range(len(matrix[0]))] for _ in range(len(matrix))]
        for r in range(len(matrix)):
            for c in range(len(matrix[0])):
                sumForCell = 0
                if r > 0:
                    sumForCell += self.prefixSums[r - 1][c]
                if c > 0:
                    sumForCell += self.prefixSums[r][c - 1]
                sumForCell += matrix[r][c]
                if r > 0 and c > 0:
                    sumForCell -= self.prefixSums[r-1][c-1]
                self.prefixSums[r][c] = sumForCell

    def sumRegion(self, row1, col1, row2, col2):
        sumForRegion = 0
        sumForRegion += self.prefixSums[row2][col2]
        if row1 > 0 and col1 > 0:
            sumForRegion += self.prefixSums[row1 - 1][col1 - 1]
        if col1 > 0:
            sumForRegion -= self.prefixSums[row2][col1 - 1]
        if row1 > 0:
            sumForRegion -= self.prefixSums[row1 - 1][col2]
        return sumForRegion

# could do with just a column prefix array
class Solution:
    def countSubmatrices(self, grid: List[List[int]], k: int) -> int:
        height = len(grid)
        width = len(grid[0])

        range2d = RangeSumQuery2d(grid)

        res = 0
        for bottomR in range(height):
            for rightC in range(width):
                isLteK = range2d.sumRegion(0, 0, bottomR, rightC) <= k
                res += isLteK
                if not isLteK:
                    break
        return res
