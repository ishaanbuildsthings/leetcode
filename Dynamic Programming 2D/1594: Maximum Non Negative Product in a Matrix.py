# https://leetcode.com/problems/maximum-non-negative-product-in-a-matrix/description/
# Problem
# You are given a m x n matrix grid. Initially, you are located at the top-left corner (0, 0), and in each step, you can only move right or down in the matrix.

# Among all possible paths starting from the top-left corner (0, 0) and ending in the bottom-right corner (m - 1, n - 1), find the path with the maximum non-negative product. The product of a path is the product of all integers in the grid cells visited along the path.

# Return the maximum non-negative product modulo 109 + 7. If the maximum product is negative, return -1.

# Notice that the modulo is performed after getting the maximum product.

# Solution, O(n*m) time and O(n*m) space
# * Could also use true DP and get min(m, n) space
# Create a HEIGHT*WIDTH*2 dp matrix, which tells us the min and max to reach that path. Check the above and left cells for each cell, starting from the bottom right.

class Solution:
    def maxProductPath(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])
        MOD = 10**9 + 7
        # for each cell, we need to know the smallest and largest possible obtainable amounts we can get by navigating from 0,0 to that cell, so memo[r][c][0] tells us the min for that path, or memo[r][c][1] tells us the max
        memo = [[[] for _ in range(WIDTH)] for _ in range(HEIGHT)]

        def dp(r, c):
            # base case, we are at the beginning
            if r == 0 and c == 0:
                return [grid[r][c], grid[r][c]]

            # memo
            if len(memo[r][c]) == 2:
                return memo[r][c]

            num = grid[r][c]
            smallest_for_this = float('inf')
            largest_for_this = float('-inf')

            # if we are not at the top, we can check above
            if r != 0:
                min_up, max_up = dp(r - 1, c)
                smallest_for_this = min(smallest_for_this, num * min_up, num * max_up)
                largest_for_this = max(largest_for_this, num * max_up, num * min_up)
            # if we are not at the left, we can check left
            if c != 0:
                min_left, max_left = dp(r, c - 1)
                smallest_for_this = min(smallest_for_this, num * min_left, num * max_left)
                largest_for_this = max(largest_for_this, num * max_left, num * min_left)

            memo[r][c] = [smallest_for_this, largest_for_this]
            return [smallest_for_this, largest_for_this]

        smallest, largest = dp(HEIGHT - 1, WIDTH - 1)

        if largest < 0:
            return -1
        return largest % MOD
