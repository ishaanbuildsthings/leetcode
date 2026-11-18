# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-bit-sum/template.py
# @operations: boxSum pointAdd pointAssign pointChmax pointChmin pointGet sumAll
# @data-structure-type: BIT
# @input: grid-3d
# @complexities:
#   boxSum: log(X)*log(Y)*log(Z)
#   pointAdd: log(X)*log(Y)*log(Z)
#   pointAssign: log(X)*log(Y)*log(Z)
#   pointChmax: log(X)*log(Y)*log(Z)
#   pointChmin: log(X)*log(Y)*log(Z)
#   pointGet: 1
#   sumAll: 1
#   build: X*Y*Z
# @memory:
#   layout: none
#   node: sm[1*X*Y*Z]
#   tags: none
#   other: vals[1*X*Y*Z]
#   note: the Fenwick tree is (X + 1) by (Y + 1) by (Z + 1), flat, 1-based



# 3D Fenwick tree (sum): point updates and any-box sums on an X x Y x Z grid, O(log X * log Y * log Z) each, with an
# eighth of a 3D segment tree's memory. A box is eight prefix queries added and subtracted. Every cell starts at 0.
# Coordinates are 0-based and boxes are inclusive: x1..x2, y1..y2, z1..z2.
class Fenwick3D:
    __slots__ = ("X", "Y", "Z", "SY", "SZ", "sm", "vals", "total")

    # O(X*Y*Z) -- X by Y by Z, every cell 0; needs X >= 1, Y >= 1 and Z >= 1, else ValueError
    def __init__(self, X, Y, Z):
        if X < 1 or Y < 1 or Z < 1:
            raise ValueError(f"Fenwick3D: needs X >= 1, Y >= 1 and Z >= 1, got X = {X}, Y = {Y}, Z = {Z}")
        self.X = X
        self.Y = Y
        self.Z = Z
        self.SY = Y + 1
        self.SZ = Z + 1
        self.sm = [0] * ((X + 1) * (Y + 1) * (Z + 1))
        self.vals = [0] * (X * Y * Z)
        self.total = 0

    # cell (x, y, z) becomes v
    def _set(self, x, y, z, v):
        X, Y, Z, SY, SZ, sm = self.X, self.Y, self.Z, self.SY, self.SZ, self.sm
        at = (x * Y + y) * Z + z
        d = v - self.vals[at]
        self.vals[at] = v
        self.total += d
        i = x + 1
        while i <= X:
            j = y + 1
            while j <= Y:
                base = (i * SY + j) * SZ
                k = z + 1
                while k <= Z:
                    sm[base + k] += d
                    k += k & -k
                j += j & -j
            i += i & -i

    # sum of the cells with all three coordinates below x, y, z
    def _prefix(self, x, y, z):
        SY, SZ, sm, res = self.SY, self.SZ, self.sm, 0
        i = x
        while i > 0:
            j = y
            while j > 0:
                base = (i * SY + j) * SZ
                k = z
                while k > 0:
                    res += sm[base + k]
                    k &= k - 1
                j &= j - 1
            i &= i - 1
        return res

    # O(1) -- the value at (x, y, z); needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else IndexError
    def pointGet(self, x, y, z):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointGet: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        return self.vals[(x * self.Y + y) * self.Z + z]

    # O(log X * log Y * log Z) -- the cell at (x, y, z) becomes v; needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else
    # IndexError
    def pointAssign(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointAssign: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        self._set(x, y, z, v)

    # O(log X * log Y * log Z) -- adds v to the cell at (x, y, z); needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else
    # IndexError
    def pointAdd(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointAdd: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        self._set(x, y, z, self.vals[(x * self.Y + y) * self.Z + z] + v)

    # O(log X * log Y * log Z) -- the cell at (x, y, z) becomes max(itself, v); needs 0 <= x < X, 0 <= y < Y and 0 <=
    # z <
    # Z, else IndexError
    def pointChmax(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointChmax: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        if v > self.vals[(x * self.Y + y) * self.Z + z]:
            self._set(x, y, z, v)

    # O(log X * log Y * log Z) -- the cell at (x, y, z) becomes min(itself, v); needs 0 <= x < X, 0 <= y < Y and 0 <=
    # z <
    # Z, else IndexError
    def pointChmin(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointChmin: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        if v < self.vals[(x * self.Y + y) * self.Z + z]:
            self._set(x, y, z, v)

    # O(log X * log Y * log Z) -- sum of the box x1..x2, y1..y2, z1..z2; needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y
    # and 0 <= z1 <= z2 < Z, else IndexError
    def boxSum(self, x1, y1, z1, x2, y2, z2):
        if not (0 <= x1 <= x2 < self.X and 0 <= y1 <= y2 < self.Y and 0 <= z1 <= z2 < self.Z):
            raise IndexError(f"boxSum: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, "
                             f"got x1 = {x1}, y1 = {y1}, z1 = {z1}, x2 = {x2}, y2 = {y2}, z2 = {z2}, X = {self.X}, "
                             f"Y = {self.Y}, Z = {self.Z}")
        p = self._prefix
        x2 += 1
        y2 += 1
        z2 += 1
        return (p(x2, y2, z2) - p(x1, y2, z2) - p(x2, y1, z2) - p(x2, y2, z1)
                + p(x1, y1, z2) + p(x1, y2, z1) + p(x2, y1, z1) - p(x1, y1, z1))

    # O(1) -- sum of the whole grid
    def sumAll(self):
        return self.total
