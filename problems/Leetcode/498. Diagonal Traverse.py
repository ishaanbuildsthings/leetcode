class Solution:
    def findDiagonalOrder(self, mat: List[List[int]]) -> List[int]:
        height = len(mat)
        width = len(mat[0])

        up = True
        r = c = 0
        res = []
        
        while True:
            res.append(mat[r][c])
            if r == height - 1 and c == width - 1:
                return res

            if up:
                if c == width - 1:
                    r += 1
                    up = not up
                elif not r:
                    c += 1
                    up = not up
                else:
                    r -= 1
                    c += 1
            else:
                if r == height - 1:
                    c += 1
                    up = not up
                elif not c:
                    r += 1
                    up = not up
                else:
                    r += 1
                    c -= 1