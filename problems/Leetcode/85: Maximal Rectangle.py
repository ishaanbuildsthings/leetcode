class Solution:
    def maximalRectangle(self, matrix: List[List[str]]) -> int:

        # O(n*m) stack + dp, using TWO separate stacks for the solveForHistRow
        # h = len(matrix)
        # w = len(matrix[0])
        # # for each cell, store its largest up-chain
        # histogram = [[0 for _ in range(w)] for _ in range(h)]
        # for r in range(h):
        #     for c in range(w):
        #         if not r:
        #             histogram[r][c] = int(matrix[r][c])
        #         else:
        #             if matrix[r][c] == '1':
        #                 histogram[r][c] = 1 + histogram[r - 1][c]

        # # for each column, we want to know the first on the left that is smaller, and on the right, so we know our span if we include this
        # def solveForHistRow(histRow):
        #     leftSmaller = [None] * w
        #     stack = []
        #     # 1 2 3 4 5 6 7 3
        #     # we pop until we hit a smaller one on the left
        #     for c in range(w):
        #         while stack and histRow[c] <= histRow[stack[-1]]:
        #             poppedI = stack.pop()
        #         if stack:
        #             leftSmaller[c] = stack[-1]
        #         stack.append(c)
            
        #     rightSmaller = [None] * w
        #     stack = []
        #     for c in range(w - 1, -1, -1):
        #         while stack and histRow[c] <= histRow[stack[-1]]:
        #             poppedI = stack.pop()
        #         if stack:
        #             rightSmaller[c] = stack[-1]
        #         stack.append(c)

        #     resBiggestArea = 0
        #     for c in range(w):
        #         leftCutoff = leftSmaller[c] if leftSmaller[c] is not None else -1
        #         rightCutoff = rightSmaller[c] if rightSmaller[c] is not None else w
        #         span = (rightCutoff - 1) - (leftCutoff + 1) + 1
        #         area = (span * histRow[c])
        #         resBiggestArea = max(resBiggestArea, area)
            
        #     return resBiggestArea
            
        # return max(solveForHistRow(row) for row in histogram)
        

        # O(n*m) stack + dp, using ONE stack for the solveForHistRow (confusing)
        height = len(matrix)
        width = len(matrix[0])

        # create a mapping for each cell which is the number of contiguous 1s above it
        heightMatrix = [row[:] for row in matrix]
        for c in range(width):
            streak = 0
            for r in range(height):
                streak = 0 if matrix[r][c] == '0' else streak + 1
                heightMatrix[r][c] = streak

        # copied from largest histogram leetcode problem, I use this to improve my efficiency from cubed to squared
        def largestRectangleArea(heights: List[int]) -> int:
            heights.append(0)
            stack = [-1]
            ans = 0
            for i in range(len(heights)):
                while heights[i] < heights[stack[-1]]:
                    h = heights[stack.pop()]
                    w = i - 1 - stack[-1]
                    ans = max(ans, h * w)
                stack.append(i)
            heights.pop() # clear out the 0
            return ans

        res = 0
        # fix the bottom left corner
        for r in range(height):
            row = heightMatrix[r]
            largest = largestRectangleArea(row)
            res = max(res, largest)
        return res