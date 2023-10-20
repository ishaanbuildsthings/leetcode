# https://leetcode.com/problems/difference-between-ones-and-zeros-in-row-and-column/description/
# difficulty: medium

# Problem
# You are given a 0-indexed m x n binary matrix grid.

# A 0-indexed m x n difference matrix diff is created with the following procedure:

# Let the number of ones in the ith row be onesRowi.
# Let the number of ones in the jth column be onesColj.
# Let the number of zeros in the ith row be zerosRowi.
# Let the number of zeros in the jth column be zerosColj.
# diff[i][j] = onesRowi + onesColj - zerosRowi - zerosColj
# Return the difference matrix diff.

# Solution, O(n * m) time and space, get the counts of everything then create the result

class Solution:
    def onesMinusZeros(self, grid: List[List[int]]) -> List[List[int]]:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        rowOnes = defaultdict(int)
        colOnes = defaultdict(int)

        for r in range(HEIGHT):
            for c in range(WIDTH):
                if grid[r][c] == 1:
                    rowOnes[r] += 1
                    colOnes[c] += 1

        res = [ [0 for _ in range(WIDTH)] for _ in range(HEIGHT) ]
        for r in range(HEIGHT):
            for c in range(WIDTH):
                rOnes = rowOnes[r]
                rZeroes = WIDTH - rOnes
                cOnes = colOnes[c]
                cZeroes = HEIGHT - cOnes
                diff = rOnes + cOnes - rZeroes - cZeroes
                res[r][c] = diff

        return res