# https://leetcode.com/problems/available-captures-for-rook/description/
# difficulty: easy

# Problem
# On an 8 x 8 chessboard, there is exactly one white rook 'R' and some number of white bishops 'B', black pawns 'p', and empty squares '.'.

# When the rook moves, it chooses one of four cardinal directions (north, east, south, or west), then moves in that direction until it chooses to stop, reaches the edge of the board, captures a black pawn, or is blocked by a white bishop. A rook is considered attacking a pawn if the rook can capture the pawn on the rook's turn. The number of available captures for the white rook is the number of pawns that the rook is attacking.

# Return the number of available captures for the white rook.

# Solution, O(sidelength^2) time, O(1) space

DIRS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]
class Solution:
    def numRookCaptures(self, board: List[List[str]]) -> int:
        BOARD_SIZE = 8

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] == 'R':
                    rookR = r
                    rookC = c
                    break

        res = 0
        for rowDiff, colDiff in DIRS:
            for distance in range(1, BOARD_SIZE + 1):
                newRow = (rowDiff * distance) + rookR
                newCol = (colDiff * distance) + rookC
                # out of bounds
                if newRow < 0 or newRow == BOARD_SIZE or newCol < 0 or newCol == BOARD_SIZE:
                    break
                # piece
                if board[newRow][newCol] == 'p':
                    res += 1
                    break
                if board[newRow][newCol] == 'B':
                    break
        return res
