# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-bit-corner-max-gtegtegte/template.py
# @operations: maxAll maxGteGteGte pointChmax
# @data-structure-type: BIT
# @input: grid-3d
# @empty-cells: yes
# @complexities:
#   maxAll: 1
#   maxGteGteGte: log(X)*log(Y)*log(Z)
#   pointChmax: log(X)*log(Y)*log(Z)
#   build: X*Y*Z
# @memory:
#   layout: none
#   node: tGteGteGte[1*X*Y*Z]
#   tags: none
#   other: none
#   note: one Fenwick tree per corner direction, (X + 1) by (Y + 1) by (Z + 1), flat; the >= direction is the same tree with every axis mirrored

NEG = float("-inf")  # an empty cell


# 3D corner max with a Fenwick tree: pointChmax at a cell and the max over every cell whose three coordinates are all
# <= (or all >=) the given ones, O(log X * log Y * log Z) each, with an eighth of a 3D segment tree's memory per
# direction. This works because values only move one way: a cell can only go up; for a cell that can move both ways,
# or for boxes that aren't corners, use the 3D segment tree. Every cell starts empty and queries only see set cells.
# Coordinates are 0-based. A max over no set cell is None.
class CornerMaxFenwick3D:
    __slots__ = ("X", "Y", "Z", "SY", "SZ", "top", "tGteGteGte")

    # O(X*Y*Z) -- X by Y by Z, every cell empty; needs X >= 1, Y >= 1 and Z >= 1, else ValueError
    def __init__(self, X, Y, Z):
        if X < 1 or Y < 1 or Z < 1:
            raise ValueError(f"CornerMaxFenwick3D: needs X >= 1, Y >= 1 and Z >= 1, got X = {X}, Y = {Y}, Z = {Z}")
        self.X = X
        self.Y = Y
        self.Z = Z
        self.SY = Y + 1
        self.SZ = Z + 1
        self.top = NEG
        self.tGteGteGte = [NEG] * ((X + 1) * (Y + 1) * (Z + 1))

    # O(log X * log Y * log Z) -- the cell at (x, y, z) becomes max(itself, v); an empty cell becomes v; needs 0 <= x
    # < X,
    # 0 <= y < Y and 0 <= z < Z, else IndexError
    def pointChmax(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointChmax: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        X, Y, Z, SY, SZ = self.X, self.Y, self.Z, self.SY, self.SZ
        if v > self.top:
            self.top = v
        t = self.tGteGteGte
        i = X - x
        while i <= X:
            j = Y - y
            while j <= Y:
                base = (i * SY + j) * SZ
                k = Z - z
                while k <= Z:
                    if v > t[base + k]:
                        t[base + k] = v
                    k += k & -k
                j += j & -j
            i += i & -i

    # O(log X * log Y * log Z) -- max of the set cells with all three coordinates >= x, y, z (None if there are none);
    # needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else IndexError
    def maxGteGteGte(self, x, y, z):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"maxGteGteGte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        SY, SZ, t, res = self.SY, self.SZ, self.tGteGteGte, NEG
        j0 = self.Y - y
        k0 = self.Z - z
        i = self.X - x
        while i > 0:
            j = j0
            while j > 0:
                base = (i * SY + j) * SZ
                k = k0
                while k > 0:
                    cand = t[base + k]
                    if cand > res:
                        res = cand
                    k &= k - 1
                j &= j - 1
            i &= i - 1
        return None if res == NEG else res

    # O(1) -- max of every set cell (None if there are none)
    def maxAll(self):
        return None if self.top == NEG else self.top
