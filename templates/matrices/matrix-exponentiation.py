MOD = 10**9 + 7


# A[x, y] @ B[y, z] = C[x, z]
# O(x*y*z)
def matMul(A, B):
    colsB = list(zip(*B))
    C = []
    for rowA in A:
        newRow = []
        for colB in colsB:
            newRow.append(sum(a * b for a, b in zip(rowA, colB)) % MOD)
        C.append(newRow)
    return C

# vec[1, x] @ mat[x, y] = vec[1, y]
# O(x*y)
def vecMatMul(vec, M):
    result = []
    for colM in zip(*M):
        result.append(sum(x * y for x, y in zip(vec, colM)) % MOD)
    return result

# mat[x, x] ^ power
# O(x^3) * log(power)
def matPow(M, p):
    size = len(M)
    result = [[int(i == j) for j in range(size)] for i in range(size)]
    while p > 0:
        if p & 1:
            result = matMul(result, M)
        M = matMul(M, M)
        p >>= 1
    return result