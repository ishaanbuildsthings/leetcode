# https://leetcode.com/problems/maximum-side-length-of-a-square-with-sum-less-than-or-equal-to-threshold/description/
# difficulty: medium
# tags: range query

# Problem
# Given a m x n matrix mat and an integer threshold, return the maximum side-length of a square with a sum less than or equal to threshold or return 0 if there is no such square.

# Solution, the max length is min(m.n), so binary search on that then test m*n cells, O(log(min(m,n)) * m*n) time and O(m*n) space

class Solution:
    def maxSideLength(self, MATRIX: List[List[int]], threshold: int) -> int:

        # ______________________________________________________________________
        # IMMUTABLE RANGE SUM 2D QUERY TEMPLATE
        # Gets the sum for a rectange range query in O(1), after O(n*m) preprocessing
        # Variables:
        # MATRIX - replace with the 2d matrix we need to query

        HEIGHT = len(MATRIX)
        WIDTH = len(MATRIX[0])
        # each cell should store the sum for the square from 0,0 to that cell
        prefix_sums = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        for r in range(HEIGHT):
            for c in range(WIDTH):
                # the sum is the left prefix plus the top prefix plus the number, minus the up left prefix
                sum_for_cell = 0
                if r > 0:
                    sum_for_cell += prefix_sums[r - 1][c]
                if c > 0:
                    sum_for_cell += prefix_sums[r][c - 1]
                sum_for_cell += MATRIX[r][c]
                if r > 0 and c > 0:
                    sum_for_cell -= prefix_sums[r-1][c-1]
                prefix_sums[r][c] = sum_for_cell

        # (row1, col1) form the top left point of the rectangle, (row2, col2) bottom right
        def sumRegion(row1, col1, row2, col2) -> int:
            # the sum for a region is the bottom right prefix, plus a top left corner prefix, minus a left and a top prefix
            sum_for_region = 0
            sum_for_region += prefix_sums[row2][col2]
            if row1 > 0 and col1 > 0:
                sum_for_region += prefix_sums[row1 - 1][col1 - 1]
            if col1 > 0:
                sum_for_region -= prefix_sums[row2][col1 - 1]
            if row1 > 0:
                sum_for_region -= prefix_sums[row1 - 1][col2]
            return sum_for_region

        res = 0
        l = 1
        r = min(HEIGHT, WIDTH)
        while l <= r:
            sideLength = (r + l) // 2
            validFound = False
            for row in range(HEIGHT - sideLength + 1):
                for col in range(WIDTH - sideLength + 1):
                    regionSum = sumRegion(row, col, row + sideLength - 1, col + sideLength - 1)
                    if regionSum <= threshold:
                        validFound = True
            if validFound:
                l = sideLength + 1
            else:
                r = sideLength - 1
        return r