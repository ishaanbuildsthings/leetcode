class Solution:
    def countBattleships(self, board: List[List[str]]) -> int:
        res = 0
        for r in range(len(board)):
            for c in range(len(board[0])):
                if board[r][c] == 'X':
                    res += (((not r) or board[r-1][c] == '.') and ((not c) or board[r][c-1] == '.'))
        return res