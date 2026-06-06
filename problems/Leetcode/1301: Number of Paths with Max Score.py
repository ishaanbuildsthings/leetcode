# https://leetcode.com/problems/number-of-paths-with-max-score/
# Difficulty: Hard
# Tags: dynamic programming 2d

# Problem
# You are given a square board of characters. You can move on the board starting at the bottom right square marked with the character 'S'.

# You need to reach the top left square marked with the character 'E'. The rest of the squares are labeled either with a numeric character 1, 2, ..., 9 or with an obstacle 'X'. In one move you can go up, left or up-left (diagonally) only if there is no obstacle there.

# Return a list of two integers: the first integer is the maximum sum of numeric characters you can collect, and the second is the number of such paths that you can take to get that maximum sum, taken modulo 10^9 + 7.

# In case there is no path, return [0, 0].

# Solution, O(n*m) time and O(n*m) space
# For each cell, consider the 3 cells we can move to. Find the max score, and get the summed paths. Each dp state stores its max score and number of paths.

class Solution:
    def pathsWithMaxScore(self, board: List[str]) -> List[int]:
        MOD = 10**9 + 7
        @cache
        def dp(r, c):
            # base case
            if r == 0 and c == 0:
                return [0, 1] # max score and number of paths

            maxScoreForThis = float('-inf')
            pathsForThis = 0

            diffs = [ [-1, 0], [0, -1], [-1, -1] ]
            for rowDiff, colDiff in diffs:
                newRow = r + rowDiff
                newCol = c + colDiff
                if newRow < 0 or newCol < 0:
                    continue
                if board[newRow][newCol] == 'X':
                    continue
                maxScoreForAdj, numPathsForAdj = dp(newRow, newCol)
                if not (newRow == 0 and newCol == 0):
                    maxScoreForAdj += int(board[newRow][newCol])
                if maxScoreForAdj > maxScoreForThis:
                    maxScoreForThis = maxScoreForAdj
                    pathsForThis = numPathsForAdj
                elif maxScoreForAdj == maxScoreForThis:
                    pathsForThis += numPathsForAdj
                    pathsForThis = pathsForThis % MOD
            return [maxScoreForThis, pathsForThis]

        res = dp(len(board) - 1, len(board[0]) - 1)
        if res[0] == float(-inf):
            return [0, 0]
        return res