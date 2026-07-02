class Solution:
    def checkMove(self, board: List[List[str]], rMove: int, cMove: int, color: str) -> bool:
        if board[rMove][cMove] != '.':
            return False
        
        target = 'B' if color == 'W' else 'W'
        

        for rowDiff, colDiff in [[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,1],[1,-1],[-1,-1]]:
            nr = rMove + rowDiff
            nc = cMove + colDiff
            if nr < 0 or nr == len(board) or nc < 0 or nc == len(board[0]):
                continue
            if board[nr][nc] != target:
                continue
            for distance in range(2, 8):
                nr = rMove + (distance * rowDiff)
                nc = cMove + (distance * colDiff)
                if nr < 0 or nr == len(board) or nc < 0 or nc == len(board[0]):
                    break
                if board[nr][nc] == '.':
                    break
                if board[nr][nc] == target:
                    continue
                return True
        
        return False