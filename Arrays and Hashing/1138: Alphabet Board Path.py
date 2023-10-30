# https://leetcode.com/problems/alphabet-board-path/description/
# difficulty: medium

# Problem
# On an alphabet board, we start at position (0, 0), corresponding to character board[0][0].

# Here, board = ["abcde", "fghij", "klmno", "pqrst", "uvwxy", "z"], as shown in the diagram below.



# We may make the following moves:

# 'U' moves our position up one row, if the position exists on the board;
# 'D' moves our position down one row, if the position exists on the board;
# 'L' moves our position left one column, if the position exists on the board;
# 'R' moves our position right one column, if the position exists on the board;
# '!' adds the character board[r][c] at our current position (r, c) to the answer.
# (Here, the only positions that exist on the board are positions with letters on them.)

# Return a sequence of moves that makes our answer equal to target in the minimum number of moves.  You may return any path that does so.

# Solution, O(target) time. We get coordinates and move in that direction. Edge case for not moving out of bounds around the z. O(target).

BOARD = ['abcde', 'fghij', 'klmno', 'pqrst', 'uvwxy', 'z']
POSITIONS = {} # maps a letter to [r, c]
for r in range(len(BOARD)):
    word = BOARD[r]
    for c in range(len(word)):
        char = word[c]
        POSITIONS[char] = [r, c]


class Solution:
    def alphabetBoardPath(self, target: str) -> str:
        resArr = []
        row = 0
        col = 0
        for targetChar in target:
            targetCharRow, targetCharCol = POSITIONS[targetChar]
            rightMovements = targetCharCol - col
            downMovements = targetCharRow - row
            # if we are going up, we should go up first, if we are going down, we should go left first, due to the z
            if downMovements < 0:
                downMovements += 1
                resArr.append('U')
            else:
                if rightMovements < 0:
                    rightMovements += 1
                    resArr.append('L')

            for _ in range(abs(rightMovements)):
                if rightMovements < 0:
                    resArr.append('L')
                else:
                    resArr.append('R')
            for _ in range(abs(downMovements)):
                if downMovements < 0:
                    resArr.append('U')
                else:
                    resArr.append('D')
            row = targetCharRow
            col = targetCharCol
            resArr.append('!')
        return ''.join(resArr)