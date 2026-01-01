n = int(input())
MOD = 10**9 + 7

if n <= 1:
    print(n)
    exit()

vec = [1, 0] # initial state vector is F[1] is 1, F[0] is 0

steps = n - 1 # we need to progress this many steps via matrix exponentiation

mat = [
    [1, 1],
    [1, 0]
]

def matMul(A, B):
    n = 2
    C = [[0]*n for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        Ci = C[i]
        for k in range(n):
            if Ai[k] == 0:
                continue
            a = Ai[k]
            Bk = B[k]
            for j in range(n):
                Ci[j] = (Ci[j] + a * Bk[j]) % MOD
    return C

def matVecMul(A, v):
    n = 2
    out = [0]*n
    for i in range(n):
        s = 0
        Ai = A[i]
        for k in range(n):
            s = (s + Ai[k] * v[k]) % MOD
        out[i] = s
    return out

def matPow(M, e):
    activeBase = M
    n = 2
    # identity matrix
    res = [[0]*n for _ in range(n)]
    for i in range(n):
        res[i][i] = 1
    # loop through each bit from small to large
    while e > 0:
        # if the bit is set, we multiply our matrix by 2^that bit
        if e & 1:
            res = matMul(res, activeBase)
        # double the base for the next loop
        activeBase = matMul(activeBase, activeBase)
        e >>= 1
    return res

# When you multiply a matrix by a column vector that is "1 in position 0 and 0 elsewhere", the result is just the 0th column of the matrix. So we could skip the matVecMul here and just take the first column.
vec2 = matVecMul(matPow(mat, steps), vec)
print(vec2[0])
