class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:


        # O(n^2) stack + dp
        h = len(matrix)
        w = len(matrix[0])
        # for each cell, store its largest up-chain
        histogram = [[0 for _ in range(w)] for _ in range(h)]
        for r in range(h):
            for c in range(w):
                if not r:
                    histogram[r][c] = int(matrix[r][c])
                else:
                    if matrix[r][c] == '1':
                        histogram[r][c] = 1 + histogram[r - 1][c]

        # for each column, we want to know the first on the left that is smaller, and on the right, so we know our span if we include this
        def solveForHistRow(histRow):
            leftSmaller = [None] * w
            stack = []
            # 1 2 3 4 5 6 7 3
            # we pop until we hit a smaller one on the left
            for c in range(w):
                while stack and histRow[c] <= histRow[stack[-1]]:
                    poppedI = stack.pop()
                if stack:
                    leftSmaller[c] = stack[-1]
                stack.append(c)
            
            rightSmaller = [None] * w
            stack = []
            for c in range(w - 1, -1, -1):
                while stack and histRow[c] <= histRow[stack[-1]]:
                    poppedI = stack.pop()
                if stack:
                    rightSmaller[c] = stack[-1]
                stack.append(c)

            resBiggestArea = 0
            for c in range(w):
                leftCutoff = leftSmaller[c] if leftSmaller[c] is not None else -1
                rightCutoff = rightSmaller[c] if rightSmaller[c] is not None else w
                span = (rightCutoff - 1) - (leftCutoff + 1) + 1
                area = min(span, histRow[c]) ** 2
                resBiggestArea = max(resBiggestArea, area)
            
            return resBiggestArea
            
        return max(solveForHistRow(row) for row in histogram)
        
        
            

        # O(n^2), iterate on bottom right cell, size of square is the biggest square is a function of left cell, up cell, left-up cell
        # can space optimize to n

        # res = 0
        # h = len(matrix)
        # w = len(matrix[0])
        # dp = [[0 for _ in range(w)] for _ in range(h)]
        # for r in range(h):
        #     for c in range(w):
        #         if matrix[r][c] == '1' and r > 0 and c > 0 and matrix[r][c] == matrix[r-1][c] == matrix[r][c-1] == matrix[r-1][c-1]:
        #             bottle = min(dp[r][c-1], dp[r-1][c], dp[r-1][c-1])
        #             dp[r][c] = 1 + bottle
        #         else:
        #             dp[r][c] = int(matrix[r][c])
        #         res = max(res, dp[r][c])
        # return res ** 2



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