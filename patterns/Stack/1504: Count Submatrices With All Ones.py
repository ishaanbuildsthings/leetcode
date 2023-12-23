# https://leetcode.com/problems/count-submatrices-with-all-ones/description/
# difficulty: medium
# tags: stack

# Problem
# Given an m x n binary matrix mat, return the number of submatrices that have all ones.

# Solution, cubed time. I made a new table which has the # of contiguous 1s above it. For each cell I fixed it as the bottom left then iterated right. We can also do it in squared time using a stack, but it is really clever, I need to think about it more or look at the idea. Similar to largest rectangle in histogram but I think it might be harder since we are counting rectangles.

class Solution:
    def numSubmat(self, mat: List[List[int]]) -> int:
        height = len(mat)
        width = len(mat[0])

        aboveMat = [row[:] for row in mat]
        for r in range(1, height):
            for c in range(width):
                if aboveMat[r][c]:
                    aboveMat[r][c] += aboveMat[r - 1][c]

        res = 0
        # fix the bottom left cell
        for r in range(height):
            for c in range(width):
                if not mat[r][c]:
                    continue
                # for each bottom left, iterate right while we can
                bottleneck = float('inf')
                for j in range(c, width):
                    bottleneck = min(bottleneck, aboveMat[r][j])
                    res += bottleneck

        return res

