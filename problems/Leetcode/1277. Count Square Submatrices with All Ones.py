class Solution:
    def countSquares(self, matrix: List[List[int]]) -> int:

        # O(n^2), iterate on the bottom right cell, the biggest square is a function of left cell, up cell, left-up cell
        res = 0
        h = len(matrix)
        w = len(matrix[0])
        dp = [[0 for _ in range(w)] for _ in range(h)]
        for r in range(h):
            for c in range(w):
                if matrix[r][c] == 1 and r > 0 and c > 0 and matrix[r][c] == matrix[r-1][c] == matrix[r][c-1] == matrix[r-1][c-1]:
                    bottle = min(dp[r][c-1], dp[r-1][c], dp[r-1][c-1])
                    dp[r][c] = 1 + bottle
                else:
                    dp[r][c] = matrix[r][c]
                res += dp[r][c]
        return res

        # O(n^3) solution, iterate on each top left corner, for each of those scan right, finding the bottleneck vertical drop
        # height = len(matrix)
        # width = len(matrix[0])

        # dupe = [
        #     row[:] for row in matrix
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
        #             res += 1

        # return res