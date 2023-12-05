# https://leetcode.com/problems/number-of-submatrices-that-sum-to-target/description/
# difficulty: hard
# tags: prefix, lop off, range query

# Problem
# Given a matrix and a target, return the number of non-empty submatrices that sum to target.

# A submatrix x1, y1, x2, y2 is the set of all cells matrix[x][y] with x1 <= x <= x2 and y1 <= y <= y2.

# Two submatrices (x1, y1, x2, y2) and (x1', y1', x2', y2') are different if they have some coordinate that is different: for example, if x1 != x1'.

# Solution
# I do variable widths and variable starting places and then cut off from the prefix as needed. On the order of n^3 time and n^2 space.

class Solution:
    def numSubmatrixSumTarget(self, matrix: List[List[int]], target: int) -> int:
        HEIGHT = len(matrix)
        WIDTH = len(matrix[0])

        prefix = defaultdict(list) # maps a row to prefix sums
        for r in range(HEIGHT):
            running = 0
            for c in range(WIDTH):
                running += matrix[r][c]
                prefix[r].append(running)

        def querySum(prefixRow, l, r):
            if l == 0:
                return prefixRow[r]
            return prefixRow[r] - prefixRow[l - 1]

        res = 0

        for width in range(1, WIDTH + 1):
            for leftOffset in range(WIDTH - width + 1):
                l = leftOffset
                r = leftOffset + width - 1
                lopOff = defaultdict(int)
                lopOff[0] += 1 # we can always lop off nothing

                running = 0
                for i in range(HEIGHT):
                    rowAddition = querySum(prefix[i], l, r)
                    running += rowAddition
                    toCutOff = running - target
                    res += lopOff[toCutOff]
                    lopOff[running] += 1

        return res




