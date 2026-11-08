# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/matrices/ModMatrix.py
from operator import mul

MOD = 10**9 + 7


# Matrix with entries mod MOD. Row-vector convention: vec[1, x] @ M[x, y] = vec[1, y]
# M = ModMatrix([[1, 1], [1, 0]])        any ints, negatives fine (stored in [0, MOD))
# C = A @ B                 A[x, y] @ B[y, z] = C[x, z]
# v = vec @ M               [a, b] @ M -> [a', b'] (vec is a plain list)
# P = M ** p                M[k, k] ^ p
# v = M.vecPow(vec, p)      vec @ M^p
# M[i][j]                   read an entry (M.rows is the list of lists)
# fib: [1, 0] @ ModMatrix([[1, 1], [1, 0]]) ** 10 -> [89, 55]
class ModMatrix:
    __slots__ = ("rows", "n", "m")

    # O(x*y) -- from a list of lists, entries taken mod MOD
    def __init__(self, rows):
        self.rows = [[x % MOD for x in row] for row in rows]
        self.n = len(self.rows)
        self.m = len(self.rows[0]) if self.rows else 0

    @staticmethod
    def _identity(k):
        return ModMatrix._wrap([[int(i == j) for j in range(k)] for i in range(k)])

    @staticmethod
    def _wrap(rows):  # rows already in [0, MOD)
        res = ModMatrix.__new__(ModMatrix)
        res.rows = rows
        res.n = len(rows)
        res.m = len(rows[0]) if rows else 0
        return res

    def __getitem__(self, i):
        return self.rows[i]

    def __len__(self):
        return self.n

    def __repr__(self):
        return f"ModMatrix({self.rows})"

    def __eq__(self, other):
        return isinstance(other, ModMatrix) and self.rows == other.rows

    # A[x, y] @ B[y, z] = C[x, z]
    # O(x*y*z)
    def __matmul__(self, other):
        if self.m != other.n:
            raise ValueError(f"matmul shape mismatch: [{self.n}, {self.m}] @ [{other.n}, {other.m}]")
        return ModMatrix._wrap(_mulRows(self.rows, other))

    # vec[1, x] @ M[x, y] = vec[1, y], vec is a plain list (any ints)
    # O(x*y)
    def __rmatmul__(self, vec):
        if len(vec) != self.n:
            raise ValueError(f"vecmat shape mismatch: [1, {len(vec)}] @ [{self.n}, {self.m}]")
        return _mulRows([[x % MOD for x in vec]], self)[0]

    # M[k, k] ^ p, p >= 0 (p = 0 gives identity)
    # O(k^3 log p)
    def __pow__(self, p):
        if self.n != self.m:
            raise ValueError(f"matrix power needs a square matrix, got [{self.n}, {self.m}]")
        if p < 0:
            raise ValueError("matrix power needs p >= 0")
        res = None
        base = self
        while True:
            if p & 1:
                res = base if res is None else res @ base
            p >>= 1
            if not p:
                break
            base = base @ base
        return res if res is not None else ModMatrix._identity(self.n)

    # vec[1, k] @ M[k, k]^p = vec[1, k], about half the work of vec @ (M ** p) (no result matrix is built)
    # O(k^3 log p)
    def vecPow(self, vec, p):
        if self.n != self.m:
            raise ValueError(f"matrix power needs a square matrix, got [{self.n}, {self.m}]")
        if p < 0:
            raise ValueError("matrix power needs p >= 0")
        res = [x % MOD for x in vec]
        base = self
        while p:
            if p & 1:
                res = res @ base
            p >>= 1
            if p:
                base = base @ base
        return res


def _mulRows(rowsA, B):  # rowsA (entries in [0, MOD)) @ B -> list of rows
    inner = B.n
    m = B.m
    if inner <= 8:  # tiny: plain dot products are fastest
        cols = list(zip(*B.rows))
        return [[sum(map(mul, row, col)) % MOD for col in cols] for row in rowsA]
    # each row of B packed into one big int (fixed-width slots), so a row of the result is
    # sum of A[i][k] * packedRow[k], done in C by Python's big int arithmetic
    width = ((inner * (MOD - 1) ** 2).bit_length() + 7) // 8
    total = width * m
    fromBytes = int.from_bytes
    packed = [fromBytes(b"".join(x.to_bytes(width, "little") for x in row), "little") for row in B.rows]
    res = []
    for row in rowsA:
        acc = 0
        for a, p in zip(row, packed):
            if a:
                acc += a * p
        raw = acc.to_bytes(total, "little")
        res.append([fromBytes(raw[j : j + width], "little") % MOD for j in range(0, total, width)])
    return res
