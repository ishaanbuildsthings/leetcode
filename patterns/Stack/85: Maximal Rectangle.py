# https://leetcode.com/problems/maximal-rectangle/description/
# difficulty: hard
# tags: stack

# Problem
# Given a rows x cols binary matrix filled with 0's and 1's, find the largest rectangle containing only 1's and return its area.

# Solution
# A relatively naive solution is to try n*m bottom left corners, and for each one try n*m top right corners. To improve this, we can make each cell record the number of 1s above it. Now for each bottom left corner, we just iterate right, tracking the bottleneck height, this is cubed. To improve further, instead of trying every bottom left corner and scanning right, we just process each row as a histogram and find the maximal rectangle there (this is largest rectangle in histogram subproblem).
# Below is the n^2 code, below that is the n^3

class Solution:
    def maximalRectangle(self, matrix: List[List[str]]) -> int:
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

# n^3 code (still not bad)

class Solution:
    def maximalRectangle(self, matrix: List[List[str]]) -> int:
        height = len(matrix)
        width = len(matrix[0])

        heightMatrix = [row[:] for row in matrix]
        for c in range(width):
            streak = 0
            for r in range(height):
                streak = 0 if matrix[r][c] == '0' else streak + 1
                heightMatrix[r][c] = streak

        res = 0

        # fix the bottom left corner
        for r in range(height):
            for c in range(width):
                smallestHeight = float('inf')
                for i in range(c, width):
                    smallestHeight = min(smallestHeight, heightMatrix[r][i])
                    base = i - c + 1
                    res = max(res, base * smallestHeight)

        return res