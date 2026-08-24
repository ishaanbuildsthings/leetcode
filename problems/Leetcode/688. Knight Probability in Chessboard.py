class Solution:
    def knightProbability(self, n: int, k: int, row: int, column: int) -> float:
        @cache
        def dp(movesLeft, r, c):
            if r < 0 or r >= n or c < 0 or c >= n: return 0
            if movesLeft == 0: return 1
            return sum(dp(movesLeft - 1, dr + r, dc + c) / 8 for dr, dc in [[2,1],[2,-1],[1,2],[1,-2],[-1,-2],[-2,-1],[-1,2],[-2,1]])
        return dp(k, row, column)