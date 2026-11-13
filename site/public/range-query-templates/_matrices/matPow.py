# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/matPow.py

# M[x, x] ^ p, every entry mod mod (p = 0 gives the identity). M must be square; p >= 0
# matPow([[1, 1], [1, 0]], 10, 10**9 + 7) -> [[89, 55], [55, 34]]   # Fibonacci numbers
# O(x^3 * log(p))
def matPow(M, p, mod):
    size = len(M)
    if any(len(row) != size for row in M):
        raise ValueError("matPow: M must be square")
    if p < 0:
        raise ValueError(f"matPow: p = {p} is negative")

    def matMul(A, B):  # A @ B mod mod: row i of A times column j of B
        colsB = list(zip(*B))
        return [[sum(a * b for a, b in zip(rowA, colB)) % mod for colB in colsB] for rowA in A]

    result = [[int(i == j) % mod for j in range(size)] for i in range(size)]
    M = [[v % mod for v in row] for row in M]
    while p:
        if p & 1:
            result = matMul(result, M)
        M = matMul(M, M)
        p >>= 1
    return result
