class Solution:
    def findDegrees(self, matrix: list[list[int]]) -> list[int]:
        res = [0] * len(matrix)
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if matrix[i][j]:
                    res[i] += 1
        return res