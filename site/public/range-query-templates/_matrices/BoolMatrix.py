# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/matrices/BoolMatrix.py


# Boolean matrix stored as one int bitmask per row (bit j of row i = entry [i][j]), so ops run 64 entries at a time
# Row-vector convention like ModMatrix. As a graph: M[i][j] = 1 means an edge i -> j
# M = BoolMatrix([[0, 1], [0, 0]])          any truthy / falsy entries
# M = BoolMatrix.fromEdges(n, edges)        directed [a, b] edges, labels 0..n-1
# C = A @ B             C[i][j] = OR over k of (A[i][k] AND B[k][j])
# v = vec @ M           vec: list of 0/1 (a set of nodes) -> nodes one step away from it
# P = M ** p            P[i][j] = 1 if some walk i -> j has exactly p edges
# R = M.closure()       R[i][j] = 1 if j is reachable from i in 0 or more steps (R[i][i] = 1)
# M.get(i, j) / M.set(i, j, bit)
# M.rows[i]             row i as a bitmask
# M.toLists()           back to a list of lists of 0/1
# BoolMatrix.fromEdges(3, [[0, 1], [1, 2]]).closure().toLists() -> [[1, 1, 1], [0, 1, 1], [0, 0, 1]]
class BoolMatrix:
    __slots__ = ("rows", "n", "m")

    # O(x*y) -- from a list of lists
    def __init__(self, rows):
        self.n = len(rows)
        self.m = len(rows[0]) if rows else 0
        self.rows = [sum(1 << j for j, x in enumerate(row) if x) for row in rows]

    # O(n + len(edges)) -- n x n adjacency matrix of directed [a, b] edges
    @staticmethod
    def fromEdges(n, edges):
        rows = [0] * n
        for a, b in edges:
            rows[a] |= 1 << b
        return BoolMatrix._wrap(rows, n, n)

    # O(k) -- the k x k identity
    @staticmethod
    def identity(k):
        return BoolMatrix._wrap([1 << i for i in range(k)], k, k)

    @staticmethod
    def _wrap(rows, n, m):
        res = BoolMatrix.__new__(BoolMatrix)
        res.rows, res.n, res.m = rows, n, m
        return res

    # O(1) -- entry [i][j] as 0 / 1
    def get(self, i, j):
        return self.rows[i] >> j & 1

    # O(1) -- set entry [i][j] to bit (0 / 1)
    def set(self, i, j, bit):
        if bit:
            self.rows[i] |= 1 << j
        else:
            self.rows[i] &= ~(1 << j)

    # O(x*y) -- as a list of lists of 0/1
    def toLists(self):
        return [[row >> j & 1 for j in range(self.m)] for row in self.rows]

    def __repr__(self):
        return f"BoolMatrix({self.toLists()})"

    def __eq__(self, other):
        return isinstance(other, BoolMatrix) and (self.n, self.m, self.rows) == (other.n, other.m, other.rows)

    # A[x, y] @ B[y, z] = C[x, z]
    # O(x*y*z / 64)
    def __matmul__(self, other):
        if self.m != other.n:
            raise ValueError(f"matmul shape mismatch: [{self.n}, {self.m}] @ [{other.n}, {other.m}]")
        return BoolMatrix._wrap([_mulMask(row, other.rows) for row in self.rows], self.n, other.m)

    # vec[1, x] @ M[x, y] = vec[1, y], vec a list of 0/1
    # O(x*y / 64)
    def __rmatmul__(self, vec):
        if len(vec) != self.n:
            raise ValueError(f"vecmat shape mismatch: [1, {len(vec)}] @ [{self.n}, {self.m}]")
        mask = _mulMask(sum(1 << j for j, x in enumerate(vec) if x), self.rows)
        return [mask >> j & 1 for j in range(self.m)]

    # M[k, k] ^ p, p >= 0 (p = 0 gives identity)
    # O(k^3 log p / 64)
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
        return res if res is not None else BoolMatrix.identity(self.n)

    # reflexive transitive closure of M[k, k]: R[i][j] = 1 if j is reachable from i in 0 or more steps
    # O(k^3 / 64)
    def closure(self):
        if self.n != self.m:
            raise ValueError(f"closure needs a square matrix, got [{self.n}, {self.m}]")
        reach = [row | 1 << i for i, row in enumerate(self.rows)]
        for k in range(self.n):  # Warshall: allow k as a middle stop
            bit = 1 << k
            rk = reach[k]
            for i in range(self.n):
                if reach[i] & bit:
                    reach[i] |= rk
        return BoolMatrix._wrap(reach, self.n, self.n)


def _mulMask(mask, rowsB):  # OR of rowsB[k] over set bits k of mask
    acc = 0
    while mask:
        low = mask & -mask
        acc |= rowsB[low.bit_length() - 1]
        mask ^= low
    return acc
