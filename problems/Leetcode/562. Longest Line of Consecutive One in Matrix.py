class Solution:
    def longestLine(self, mat: List[List[int]]) -> int:
        height = len(mat)
        width = len(mat[0])

        def getScore(startR, startC, dR, dC):
            curr = res = 0
            r = startR
            c = startC
            while r >= 0 and c >= 0 and r < height and c < width:
                nextCell = mat[r][c]
                if nextCell:
                    curr += 1
                    res = max(res, curr)
                else:
                    curr = 0
                r += dR
                c += dC
            return res
        
        res = 0
        for row in range(height):
            # horizontal lines going right
            res = max(res, getScore(row, 0, 0, 1))
            # diagonals going down and right
            res = max(res, getScore(row, 0, 1, 1))
            # diagonals going down and left, starting at the right end
            res = max(res, getScore(row, width - 1, 1, -1))
        for col in range(width):
            # vertical lines going down
            res = max(res, getScore(0, col, 1, 0))
            # diagonals going down and right
            res = max(res, getScore(0, col, 1, 1))
            # diagonals going down and left
            res = max(res, getScore(0, col, 1, -1))
        
        return res