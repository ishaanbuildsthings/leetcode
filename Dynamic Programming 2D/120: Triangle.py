# https://leetcode.com/problems/triangle/description/
# Difficulty: Medium
# Tags: Dynamic Programming 2d, trees

# Problem

# Given a triangle array, return the minimum path sum from top to bottom.

# For each step, you may move to an adjacent number of the row below. More formally, if you are on index i on the current row, you may move to either index i or index i + 1 on the next row.

# Solution
# O(nodes) time and space, which is n^2.
# Solve every r, c subproblem. If we want tabulation, you can just iterate row by row and have a table of length n.

class Solution:
    def minimumTotal(self, triangle: List[List[int]]) -> int:
        HEIGHT = len(triangle)
        @cache
        def dfs(r, c):
            # base case
            if r == HEIGHT:
                return 0

            pathSumLeft = triangle[r][c] + dfs(r + 1, c)
            pathSumRight = triangle[r][c] + dfs(r + 1, c + 1)

            return min(pathSumLeft, pathSumRight)
        return dfs(0, 0)