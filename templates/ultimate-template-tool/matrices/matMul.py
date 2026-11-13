# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/matMul.py

# A[x, y] @ B[y, z] = C[x, z], every entry mod mod: C[i][j] = row i of A times column j of B
# A's column count must equal B's row count. Entries may be any ints (negative ones come back reduced into [0, mod))
# matMul([[1, 2], [3, 4]], [[5, 6], [7, 8]], 10**9 + 7) -> [[19, 22], [43, 50]]
# O(x * y * z)
def matMul(A, B, mod):
    if A and len(A[0]) != len(B):
        raise ValueError(f"matMul: A has {len(A[0])} columns but B has {len(B)} rows")
    colsB = list(zip(*B))
    return [[sum(a * b for a, b in zip(rowA, colB)) % mod for colB in colsB] for rowA in A]
