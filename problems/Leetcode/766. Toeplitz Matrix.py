class Solution:
    def isToeplitzMatrix(self, matrix: List[List[int]]) -> bool:
        h = len(matrix)
        w = len(matrix[0])

        # left side start
        for r in range(h):
            for dist in range(max(h, w)):
                if r + dist == h or dist == w:
                    break
                if matrix[r + dist][dist] != matrix[r][0]:
                    return False

        # top side start
        for c in range(1, w):
            for dist in range(max(h, w)):
                if c + dist == w or dist == h:
                    break
                if matrix[dist][c + dist] != matrix[0][c]:
                    return False
        
        return True
