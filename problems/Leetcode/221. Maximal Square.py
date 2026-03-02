class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:

        # O(n^2), iterate on bottom right cell, size of square is the biggest square is a function of left cell, up cell, left-up cell
        # can space optimize to n

        res = 0
        h = len(matrix)
        w = len(matrix[0])
        dp = [[0 for _ in range(w)] for _ in range(h)]
        for r in range(h):
            for c in range(w):
                if matrix[r][c] == '1' and r > 0 and c > 0 and matrix[r][c] == matrix[r-1][c] == matrix[r][c-1] == matrix[r-1][c-1]:
                    bottle = min(dp[r][c-1], dp[r-1][c], dp[r-1][c-1])
                    dp[r][c] = 1 + bottle
                else:
                    dp[r][c] = int(matrix[r][c])
                res = max(res, dp[r][c])
        return res ** 2

        # O(n^3) dp, iterate on top left corner, for each of those scan right tracking the bottleneck
        # height = len(matrix)
        # width = len(matrix[0])

        # dupe = [
        #     [int(s) for s in row] for row in matrix
        # ]

        # for r in range(1, len(dupe)):
        #     for c in range(len(dupe[0])):
        #         if dupe[r][c]:
        #             dupe[r][c] += dupe[r-1][c]
        
        # res = 0
        # for r in range(height):
        #     for c in range(width):
        #         smallestHeight = dupe[r][c]
        #         for rightEdge in range(c, width):
        #             smallestHeight = min(smallestHeight, dupe[r][rightEdge])
        #             horiz = rightEdge - c + 1
        #             if smallestHeight < horiz:
        #                 break
        #             res = max(res, horiz)

        # return res**2