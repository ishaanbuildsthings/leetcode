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
        