# https://leetcode.com/problems/lonely-pixel-i/
# difficulty: medium
# tags: functional

# Problem
# Given an m x n picture consisting of black 'B' and white 'W' pixels, return the number of black lonely pixels.

# A black lonely pixel is a character 'B' that located at a specific position where the same row and same column don't have any other black pixels.

# Solution, O(n*m) time and O(n + m) space, standard counting. An O(1) solution exists where we first get the count for the first row and column then override them with values.

class Solution:
    def findLonelyPixel(self, picture: List[List[str]]) -> int:
        # maps a row to the number of 'B' that occur
        rowCounts = { r : sum(1 for char in picture[r] if char == 'B') for r in range(len(picture)) }
        colCounts = { c : sum(1 for row in picture if row[c] == 'B') for c in range(len(picture[0])) }

        res = 0
        for r in range(len(picture)):
            for c in range(len(picture[0])):
                res += picture[r][c] == 'B' and rowCounts[r] == colCounts[c] == 1
        return res