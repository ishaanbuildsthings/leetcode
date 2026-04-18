# https://leetcode.com/problems/game-of-life/
# difficulty: medium

# Solution, O(n*m) time O(1) space

class Solution:
    def gameOfLife(self, board: List[List[int]]) -> None:
        """
        Do not return anything, modify board in-place instead.
        """

        # 2 means was 0, will become 0
        # 3 means was 0, will become 1
        # 4 means was 1, will become 0
        # 5 means was 1, will become 1
        # you could just use 2 new values, instead of 4, and have the 0 and 1 encode as things

        height = len(board)
        width = len(board[0])

        DIFFS = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0: continue
                DIFFS.append([i, j])

        def getLiveNeighbors(r, c):
            liveNeighbors = 0
            for rowDiff, colDiff in DIFFS:
                newRow = r + rowDiff
                newCol = c + colDiff
                if newRow < 0 or newRow == height or newCol < 0 or newCol == width:
                    continue
                liveNeighbors += board[newRow][newCol] in [1, 4, 5]
            return liveNeighbors

        for r in range(height):
            for c in range(width):
                if board[r][c] == 0:
                    board[r][c] = 2 if getLiveNeighbors(r, c) != 3 else 3
                elif board[r][c] == 1:
                    board[r][c] = 5 if getLiveNeighbors(r, c) in [2, 3] else 4

        for r in range(height):
            for c in range(width):
                board[r][c] = 0 if board[r][c] in [2, 4] else 1


