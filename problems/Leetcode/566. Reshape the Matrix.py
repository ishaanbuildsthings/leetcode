class Solution:
    def matrixReshape(self, mat: List[List[int]], r1: int, c1: int) -> List[List[int]]:
        height = len(mat)
        width = len(mat[0])
        if height * width != r1 * c1:
            return mat
        
        res = [[None] * c1 for _ in range(r1)]
        resR = resC = 0
        for r in range(height):
            for c in range(width):
                val = mat[r][c]
                res[resR][resC] = val
                resC += 1
                if resC == c1:
                    resC = 0
                    resR += 1
        return res