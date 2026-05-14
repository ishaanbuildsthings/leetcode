# https://leetcode.com/problems/the-knights-tour/
# difficulty: medium
# tags: backtracking

# Problem
# Given two positive integers m and n which are the height and width of a 0-indexed 2D-array board, a pair of positive integers (r, c) which is the starting position of the knight on the board.

# Your task is to find an order of movements for the knight, in a manner that every cell of the board gets visited exactly once (the starting cell is considered visited and you shouldn't visit it again).

# Return the array board in which the cells' values show the order of visiting the cell starting from 0 (the initial place of the knight).

# Note that a knight can move from cell (r1, c1) to cell (r2, c2) if 0 <= r2 <= m - 1 and 0 <= c2 <= n - 1 and min(abs(r1 - r2), abs(c1 - c2)) = 1 and max(abs(r1 - r2), abs(c1 - c2)) = 2.

# Solution, O(m*n)^8 time and m*n space, standard backtracking, really its less because most cells cannot move to 8 spots

class Solution:
    def tourOfKnight(self, m: int, n: int, r: int, c: int) -> List[List[int]]:
        HEIGHT = m
        WIDTH = n
        DIFFS = [ [1,2], [-1, 2], [1, -2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1] ]
        seen = set()
        seen.add(r * WIDTH + c)
        res = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
        res[r][c] = 0
        def backtrack(r, c, visitedCount):

            # base case, everything is visited
            if visitedCount == HEIGHT * WIDTH:
                return True

            for rowDiff, colDiff in DIFFS:
                newRow = rowDiff + r
                newCol = colDiff + c
                adjKey = newRow * WIDTH + newCol
                if adjKey in seen:
                    continue
                if newRow < 0 or newRow >= HEIGHT or newCol < 0 or newCol >= WIDTH:
                    continue
                seen.add(adjKey)
                res[newRow][newCol] = visitedCount
                adjResult = backtrack(newRow, newCol, visitedCount + 1)
                if adjResult:
                    return True
                seen.remove(adjKey)
                res[newRow][newCol] = None

        backtrack(r, c, 1)
        return res


