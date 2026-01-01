n = int(input())

MOD = 10**9 + 7

# [newA0]   [ ? ? ? ? ? ? ] [a0]
# [newA1] = [ ? ? ? ? ? ? ] [a1]
# [newA2]   [ ? ? ? ? ? ? ] [a2]
# [newA3]   [ ? ? ? ? ? ? ] [a3]
# [newA4]   [ ? ? ? ? ? ? ] [a4]
# [newA5]   [ ? ? ? ? ? ? ] [a5]

mat = [
    [1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0],
]

vector = [1, 0, 0, 0, 0, 0]

def matMul(A, B):
    n = 6
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

def matPow(M, e):
    activeBase = M
    n = 6
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

def matVecMul(A, v):
    n = 6
    out = [0]*n
    for i in range(n):
        s = 0
        Ai = A[i]
        for k in range(n):
            s = (s + Ai[k] * v[k]) % MOD
        out[i] = s
    return out

# When you multiply a matrix by a column vector that is “1 in position 0 and 0 elsewhere”, the result is just the 0th column of the matrix. So we could skip the matVecMul here and just tkaae the first column.
vec2 = matVecMul(matPow(mat, n), vector)
print(vec2[0])