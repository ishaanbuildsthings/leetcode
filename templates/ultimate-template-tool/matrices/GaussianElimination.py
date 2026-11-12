# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/GaussianElimination.py

MOD = 10**9 + 7  # must be prime (pivots get divided out)


# Linear algebra mod a prime MOD on plain lists of lists (any ints, negatives fine)
# determinant(M)       det of M[k, k]
# matrixRank(M)        rank of M[x, y]
# inverse(M)           inverse of M[k, k], None if it is singular
# solve(A, b)          some x with sum over j of A[i][j] * x[j] = b[i] for every row i, None if there is none
#                      (free variables are set to 0; a solvable system has MOD^(columns - rank) solutions)
# determinant([[1, 2], [3, 4]]) -> MOD - 2
# inverse([[2, 0], [0, 4]]) -> [[500000004, 0], [0, 250000002]]
# solve([[1, 1], [1, -1]], [10, 2]) -> [6, 4]
# spanning trees of a graph (Kirchhoff): determinant of the Laplacian (degree on the diagonal, -1 per edge) with any one
# row and column deleted


# det of M[k, k]
# O(k^3)
def determinant(M):
    k = len(M)
    if any(len(row) != k for row in M):
        raise ValueError("determinant needs a square matrix")
    _, pivotCols, det = _eliminate(M, k, False)
    return det if len(pivotCols) == k else 0


# rank of M[x, y]
# O(x * y * min(x, y))
def matrixRank(M):
    if not M:
        return 0
    return len(_eliminate(M, len(M[0]), False)[1])


# inverse of M[k, k] (M @ inverse(M) = identity), None if M is singular
# O(k^3)
def inverse(M):
    k = len(M)
    if any(len(row) != k for row in M):
        raise ValueError("inverse needs a square matrix")
    aug = [list(row) + [int(i == j) for j in range(k)] for i, row in enumerate(M)]
    rows, pivotCols, _ = _eliminate(aug, k, True)
    if len(pivotCols) < k:
        return None
    return [row[k:] for row in rows]


# some x (length = columns of A) with sum over j of A[i][j] * x[j] = b[i] for every row i, None if there is none
# free variables are set to 0
# O(rows * columns * min(rows, columns))
def solve(A, b):
    if len(A) != len(b):
        raise ValueError(f"solve needs one b value per row of A, got {len(A)} rows and {len(b)} values")
    cols = len(A[0]) if A else 0
    rows, pivotCols, _ = _eliminate([list(row) + [val] for row, val in zip(A, b)], cols, True)
    if any(row[cols] for row in rows[len(pivotCols) :]):  # a 0 = nonzero row
        return None
    x = [0] * cols
    for row, c in zip(rows, pivotCols):
        x[c] = row[cols]
    return x


# Gauss(-Jordan) elimination on the first numVars columns -> (rows in [0, MOD), pivot column of each pivot row, det)
# pivot rows come first, each scaled so its pivot is 1; full: clear pivot columns in every row, not just below each row
# lives in one big int (fixed-width slots) so a row update is one big int multiply-add done in C
def _eliminate(matrix, numVars, full):
    n = len(matrix)
    m = len(matrix[0]) if matrix else 0
    # a slot starts < MOD and gains at most (MOD-1)^2 per pivot before its row is reduced again
    width = ((MOD + max(1, numVars) * (MOD - 1) ** 2).bit_length() + 7) // 8
    bits = 8 * width
    mask = (1 << bits) - 1
    total = width * m
    fromBytes = int.from_bytes

    def pack(row):
        return fromBytes(b"".join(x.to_bytes(width, "little") for x in row), "little")

    def unpack(val):
        raw = val.to_bytes(total, "little")
        return [fromBytes(raw[j : j + width], "little") % MOD for j in range(0, total, width)]

    packed = [pack([x % MOD for x in row]) for row in matrix]
    pivotCols = []
    det = 1
    r = 0
    for c in range(numVars):
        if r == n:
            break
        shift = c * bits
        piv = -1
        for i in range(r, n):
            if (packed[i] >> shift & mask) % MOD:
                piv = i
                break
        if piv < 0:
            continue
        if piv != r:
            packed[piv], packed[r] = packed[r], packed[piv]
            det = (MOD - det) % MOD
        row = unpack(packed[r])
        v = row[c]
        det = det * v % MOD
        inv = pow(v, MOD - 2, MOD)
        pivotRow = pack([x * inv % MOD for x in row])
        packed[r] = pivotRow
        for i in range(0 if full else r + 1, n):
            if i != r:
                f = (packed[i] >> shift & mask) % MOD
                if f:
                    packed[i] += (MOD - f) * pivotRow
        pivotCols.append(c)
        r += 1
    return [unpack(p) for p in packed], pivotCols, det
