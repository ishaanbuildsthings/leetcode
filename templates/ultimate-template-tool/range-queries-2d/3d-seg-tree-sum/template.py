# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-seg-tree-sum/template.py
# @operations: boxSum pointAdd pointAssign pointChmax pointChmin pointGet sumAll
# @data-structure-type: seg-tree
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
#   layout: 2n-iterative
#   node: sm[8*X*Y*Z]
#   tags: none
#   other: none
#   note: one flat array per aggregate, 2X x-nodes by 2Y y-nodes by 2Z z-nodes



# 3D segment tree (sum): point updates and any-box queries on an X x Y x Z grid, O(log X * log Y * log Z) each. A
# bottom-up tree over x whose every node is a tree over y whose every node is a tree over z, in one flat array per
# aggregate (8 * X * Y * Z entries each, so the three sides have to be small: compress coordinates first). Coordinates
# are 0-based and boxes are inclusive: x1..x2, y1..y2, z1..z2. Every cell starts at 0.
class SegTree3D:
    __slots__ = ("X", "Y", "Z", "SY", "SZ", "sm")

    # O(X*Y*Z) -- X by Y by Z, every cell 0; needs X >= 1, Y >= 1 and Z >= 1, else ValueError
    def __init__(self, X, Y, Z):
        if X < 1 or Y < 1 or Z < 1:
            raise ValueError(f"SegTree3D: needs X >= 1, Y >= 1 and Z >= 1, got X = {X}, Y = {Y}, Z = {Z}")
        self.X = X
        self.Y = Y
        self.Z = Z
        self.SY = 2 * Y  # y-nodes per x-node
        self.SZ = 2 * Z  # z-nodes per y-node
        self.sm = [0] * (8 * X * Y * Z)

    # cell (x, y, z) = v, then every node above it
    def _set(self, x, y, z, v):
        X, Y, Z, SY, SZ = self.X, self.Y, self.Z, self.SY, self.SZ
        sm = self.sm
        px = x + X
        py = y + Y
        base = (px * SY + py) * SZ  # the cell's own z-tree
        sm[base + z + Z] = v
        pz = (z + Z) >> 1
        while pz:
            sm[base + pz] = sm[base + 2 * pz] + sm[base + 2 * pz + 1]
            pz >>= 1
        py >>= 1
        while py:  # the y-nodes above, still in the cell's own x
            base = (px * SY + py) * SZ
            lo = (px * SY + 2 * py) * SZ
            hi = lo + SZ
            pz = z + Z
            while pz:
                sm[base + pz] = sm[lo + pz] + sm[hi + pz]
                pz >>= 1
            py >>= 1
        px >>= 1
        step = SY * SZ
        while px:  # the x-nodes above
            py = y + Y
            while py:
                base = (px * SY + py) * SZ
                lo = (2 * px * SY + py) * SZ
                hi = lo + step
                pz = z + Z
                while pz:
                    sm[base + pz] = sm[lo + pz] + sm[hi + pz]
                    pz >>= 1
                py >>= 1
            px >>= 1

    # O(1) -- the value at (x, y, z); needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else IndexError
    def pointGet(self, x, y, z):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointGet: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        return self.sm[((x + self.X) * self.SY + y + self.Y) * self.SZ + z + self.Z]

    # O(log X * log Y * log Z) -- the cell at (x, y, z) becomes v (it may go down as well as up); needs 0 <= x < X, 0
    # <= y
    # < Y and 0 <= z < Z, else IndexError
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
        cur = self.sm[((x + self.X) * self.SY + y + self.Y) * self.SZ + z + self.Z]
        self._set(x, y, z, cur + v)

    # O(log X * log Y * log Z) -- the cell at (x, y, z) becomes max(itself, v); needs 0 <= x < X, 0 <= y < Y and 0 <=
    # z <
    # Z, else IndexError
    def pointChmax(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointChmax: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        cur = self.sm[((x + self.X) * self.SY + y + self.Y) * self.SZ + z + self.Z]
        if v > cur:
            self._set(x, y, z, v)

    # O(log X * log Y * log Z) -- the cell at (x, y, z) becomes min(itself, v); needs 0 <= x < X, 0 <= y < Y and 0 <=
    # z <
    # Z, else IndexError
    def pointChmin(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointChmin: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        cur = self.sm[((x + self.X) * self.SY + y + self.Y) * self.SZ + z + self.Z]
        if v < cur:
            self._set(x, y, z, v)

    def _sumOf(self, x1, y1, z1, x2, y2, z2):
        X, Y, Z, SY, SZ = self.X, self.Y, self.Z, self.SY, self.SZ
        sm = self.sm
        res = 0
        yl = y1 + Y
        yr = y2 + Y + 1
        zl = z1 + Z
        zr = z2 + Z + 1
        lx = x1 + X
        rx = x2 + X + 1
        while lx < rx:
            if lx & 1:
                ly = yl
                ry = yr
                while ly < ry:
                    if ly & 1:
                        base = (lx * SY + ly) * SZ
                        lz = zl
                        rz = zr
                        while lz < rz:
                            if lz & 1:
                                res += sm[base + lz]
                                lz += 1
                            if rz & 1:
                                rz -= 1
                                res += sm[base + rz]
                            lz >>= 1
                            rz >>= 1
                        ly += 1
                    if ry & 1:
                        ry -= 1
                        base = (lx * SY + ry) * SZ
                        lz = zl
                        rz = zr
                        while lz < rz:
                            if lz & 1:
                                res += sm[base + lz]
                                lz += 1
                            if rz & 1:
                                rz -= 1
                                res += sm[base + rz]
                            lz >>= 1
                            rz >>= 1
                    ly >>= 1
                    ry >>= 1
                lx += 1
            if rx & 1:
                rx -= 1
                ly = yl
                ry = yr
                while ly < ry:
                    if ly & 1:
                        base = (rx * SY + ly) * SZ
                        lz = zl
                        rz = zr
                        while lz < rz:
                            if lz & 1:
                                res += sm[base + lz]
                                lz += 1
                            if rz & 1:
                                rz -= 1
                                res += sm[base + rz]
                            lz >>= 1
                            rz >>= 1
                        ly += 1
                    if ry & 1:
                        ry -= 1
                        base = (rx * SY + ry) * SZ
                        lz = zl
                        rz = zr
                        while lz < rz:
                            if lz & 1:
                                res += sm[base + lz]
                                lz += 1
                            if rz & 1:
                                rz -= 1
                                res += sm[base + rz]
                            lz >>= 1
                            rz >>= 1
                    ly >>= 1
                    ry >>= 1
            lx >>= 1
            rx >>= 1
        return res

    # O(log X * log Y * log Z) -- sum of the box x1..x2, y1..y2, z1..z2; needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y
    # and 0
    # <= z1 <= z2 < Z, else IndexError
    def boxSum(self, x1, y1, z1, x2, y2, z2):
        if not (0 <= x1 <= x2 < self.X and 0 <= y1 <= y2 < self.Y and 0 <= z1 <= z2 < self.Z):
            raise IndexError(f"boxSum: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, "
                             f"got x1 = {x1}, y1 = {y1}, z1 = {z1}, x2 = {x2}, y2 = {y2}, z2 = {z2}, X = {self.X}, "
                             f"Y = {self.Y}, Z = {self.Z}")
        return self._sumOf(x1, y1, z1, x2, y2, z2)

    # O(1) -- sum of the whole grid
    def sumAll(self):
        return self.sm[(self.SY + 1) * self.SZ + 1]
