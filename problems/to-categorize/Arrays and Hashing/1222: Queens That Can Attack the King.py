# https://leetcode.com/problems/queens-that-can-attack-the-king/description/
# Difficulty: Medium

# Problem
# On a 0-indexed 8 x 8 chessboard, there can be multiple black queens ad one white king.

# You are given a 2D integer array queens where queens[i] = [xQueeni, yQueeni] represents the position of the ith black queen on the chessboard. You are also given an integer array king of length 2 where king = [xKing, yKing] represents the position of the white king.

# Return the coordinates of the black queens that can directly attack the king. You may return the answer in any order.

# Solution, O(1) time and space
# Iterate out until hitting a boundary or a queen. Clever style of iteration, create the diff first then iterate that many steps.

class Solution:
    def queensAttacktheKing(self, queens: List[List[int]], king: List[int]) -> List[List[int]]:
        HEIGHT = 8
        WIDTH = 8
        queenSet = set()
        for queenRow, queenCol in queens:
            queenSet.add(queenRow * WIDTH + queenCol)

        kingRow, kingCol = king
        res = []
        for rowOffset in [-1, 0, 1]:
            for colOffset in [-1, 0, 1]:
                for steps in range(1, 8):
                    row = kingRow + (rowOffset * steps)
                    col = kingCol + (colOffset * steps)
                    # skip out of bounds
                    if row < 0 or row == HEIGHT or col < 0 or col == WIDTH:
                        break
                    key = row * WIDTH + col
                    if key in queenSet:
                        res.append([row, col])
                        break
        return res