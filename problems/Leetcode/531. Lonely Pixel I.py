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