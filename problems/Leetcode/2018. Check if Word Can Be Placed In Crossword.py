class Solution:
    def placeWordInCrossword(self, board: List[List[str]], word: str) -> bool:
        height = len(board)
        width = len(board[0])

        def inBounds(r, c):
            return r < height and r >= 0 and c < width and c >= 0
        
        def oob(r, c):
            return not inBounds(r, c)

        for r in range(height):
            for c in range(width):
                for dir in [[1,0],[-1,0],[0,1],[0,-1]]:
                    before = r - dir[0], c - dir[1]
                    if inBounds(*before) and board[before[0]][before[1]] != '#':
                        continue
                    end = r + (len(word) - 1) * dir[0], c + (len(word) - 1) * dir[1]
                    if oob(*end):
                        continue
                    after = end[0] + dir[0], end[1] + dir[1]
                    if inBounds(*after) and board[after[0]][after[1]] != '#':
                        continue
                    fail = False
                    for steps in range(len(word)):
                        r2 = r + steps * dir[0]
                        c2 = c + steps * dir[1]
                        if board[r2][c2] in [' ', word[steps]]:
                            continue
                        else:
                            fail = True
                            break
                    if not fail:
                        return True
        
        return False