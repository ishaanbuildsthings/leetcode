def matrixExponentiate(mat, power):
    size = len(mat)
    result = [[1 if i == j else 0 for j in range(size)] for i in range(size)]
    
    def matrixMultiply(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(size)) for j in range(size)] for i in range(size)]
    
    while power > 0:
        if power % 2 == 1:
            result = matrixMultiply(result, mat)
        mat = matrixMultiply(mat, mat)
        power //= 2
    return result

def matrixVectorMultiply(mat, vec):
    size = len(mat)
    return [sum(mat[i][j] * vec[j] for j in range(size)) for i in range(size)]

class Solution:
    def tribonacci(self, n: int) -> int:
        if n == 0:
            return 0
            
        M0 = [
            [1, 1, 1],
            [1, 0, 0],
            [0, 1, 0]
        ]
        V0 = [1, 1, 0]
        Mn = matrixExponentiate(M0, n - 2)
        Vn = matrixVectorMultiply(Mn, V0)
        return Vn[0]