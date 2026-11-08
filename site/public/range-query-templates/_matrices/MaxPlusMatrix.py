# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/MaxPlusMatrix.py

NEG_INF = -4 * 10**18  # no edge / no walk; real walk weights must stay within -10**18 .. 10**18
NEG_HALF = -2 * 10**18


# (max, +) matrix: "multiply" adds weights, "add" takes the max. Row-vector convention like ModMatrix
# M[i][j] = weight of edge i -> j (NEG_INF for no edge), weights any ints (negatives fine)
# M = MaxPlusMatrix(rows)
# C = A @ B             C[i][j] = max over k of A[i][k] + B[k][j]
# v = vec @ M           v[j] = max over k of vec[k] + M[k][j] (vec[k] = best weight to reach k so far)
# P = M ** p            P[i][j] = heaviest walk i -> j with exactly p edges, NEG_INF if none
# v = M.vecPow(vec, p)  vec @ M^p
# add 0-weight self-loops (M[i][i] = max(M[i][i], 0)) to get "at most p edges"
# M[i][j]               read an entry (M.rows is the list of lists)
# MaxPlusMatrix([[NEG_INF, 3, 10], [NEG_INF, NEG_INF, 4], [NEG_INF, NEG_INF, NEG_INF]] ** 2 -> [0][2] = 7)
class MaxPlusMatrix:
    __slots__ = ("rows", "n", "m")

    # O(x*y) -- from a list of lists (NEG_INF = no edge)
    def __init__(self, rows):
        self.rows = [[x if x > NEG_HALF else NEG_INF for x in row] for row in rows]
        self.n = len(self.rows)
        self.m = len(self.rows[0]) if self.rows else 0

    # O(k^2) -- the identity: 0 on the diagonal (empty walk), NEG_INF elsewhere
    @staticmethod
    def identity(k):
        return MaxPlusMatrix([[0 if i == j else NEG_INF for j in range(k)] for i in range(k)])

    def __getitem__(self, i):
        return self.rows[i]

    def __len__(self):
        return self.n

    def __repr__(self):
        return f"MaxPlusMatrix({self.rows})"

    def __eq__(self, other):
        return isinstance(other, MaxPlusMatrix) and self.rows == other.rows

    # A[x, y] @ B[y, z] = C[x, z]
    # O(x*y*z)
    def __matmul__(self, other):
        if self.m != other.n:
            raise ValueError(f"matmul shape mismatch: [{self.n}, {self.m}] @ [{other.n}, {other.m}]")
        res = MaxPlusMatrix.__new__(MaxPlusMatrix)
        res.rows = [_mulRow(row, other.rows, other.m) for row in self.rows]
        res.n, res.m = self.n, other.m
        return res

    # vec[1, x] @ M[x, y] = vec[1, y], vec is a plain list (NEG_INF = unreachable)
    # O(x*y)
    def __rmatmul__(self, vec):
        if len(vec) != self.n:
            raise ValueError(f"vecmat shape mismatch: [1, {len(vec)}] @ [{self.n}, {self.m}]")
        return _mulRow([x if x > NEG_HALF else NEG_INF for x in vec], self.rows, self.m)

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
        return res if res is not None else MaxPlusMatrix.identity(self.n)

    # vec[1, k] @ M[k, k]^p = vec[1, k], about half the work of vec @ (M ** p)
    # O(k^3 log p)
    def vecPow(self, vec, p):
        if self.n != self.m:
            raise ValueError(f"matrix power needs a square matrix, got [{self.n}, {self.m}]")
        if p < 0:
            raise ValueError("matrix power needs p >= 0")
        res = list(vec)
        base = self
        while p:
            if p & 1:
                res = res @ base
            p >>= 1
            if p:
                base = base @ base
        return res


def _mulRow(row, rowsB, m):  # row @ B, every value either real or exactly NEG_INF
    acc = [NEG_INF] * m
    for a, brow in zip(row, rowsB):
        if a > NEG_INF:
            acc = list(map(max, acc, map(a.__add__, brow)))
    return [x if x > NEG_HALF else NEG_INF for x in acc]
