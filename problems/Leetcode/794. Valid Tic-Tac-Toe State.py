class Solution:
    def validTicTacToe(self, board: List[str]) -> bool:
        o = sum(board[r][c] == 'O' for r in range(len(board)) for c in range(len(board[0])))
        x = sum(board[r][c] == 'X' for r in range(len(board)) for c in range(len(board[0])))

        if x < o or x - o > 1:
            return False

        # invalid if there are two solved rows or two solved columns
        seen = 0
        x3 = 0
        o3 = 0
        for row in board:
            if row == 'OOO' or row == 'XXX':
                seen += 1
            x3 += row == 'XXX'
            o3 += row == 'OOO'
        if seen >= 2:
            return False
        
        seen = 0
        for c in range(3):
            col = board[0][c] + board[1][c] + board[2][c]
            if col == 'OOO' or col == 'XXX':
                seen += 1
            x3 += col == 'XXX'
            o3 += col == 'OOO'
        if seen >= 2:
            return False
        
        o3 += all(board[r][r] == 'O' for r in range(3))
        o3 += board[0][2] == board[1][1] == board[2][0] == 'O'
        x3 += all(board[r][r] == 'X' for r in range(3))
        x3 += board[0][2] == board[1][1] == board[2][0] == 'X'

        if x3 and x == o:
            return False
        if o3 and x == o + 1:
            return False
        
        return True
        

        # oxx
        # xox
        # oxo