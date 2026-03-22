class Solution:
    def findRotation(self, mat: List[List[int]], target: List[List[int]]) -> bool:
        height = len(mat)
        width = len(mat[0])

        def rot():
            for r in range(len(mat)):
                for c in range(r, len(mat)):
                    mat[r][c], mat[c][r] = mat[c][r], mat[r][c]
            for row in mat:
                row.reverse()
        
        def same():
            return all(r1 == r2 for r1, r2 in zip(mat, target))
        
        if same():
            return True
        for _ in range(3):
            rot()
            if same():
                return True
        return False


