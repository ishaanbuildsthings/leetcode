# https://leetcode.com/problems/determine-color-of-a-chessboard-square/description/
# difficulty: easy

# Problem
# You are given coordinates, a string that represents the coordinates of a square of the chessboard. Below is a chessboard for your reference.



# Return true if the square is white, and false if the square is black.

# The coordinate will always represent a valid chessboard square. The coordinate will always have the letter first, and the number second.

# Solution, O(1) time and space

class Solution:
    def squareIsWhite(self, coordinates: str) -> bool:
        return ord(coordinates[0]) % 2 != int(coordinates[1]) % 2