# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-seg-tree-sum-max/template.py
# @operations: boxMax boxSum maxAll maxGteGteGte maxLteLteLte pointAdd pointAssign pointChmax pointChmin pointGet sumAll sumGteGteGte sumLteLteLte
# @data-structure-type: seg-tree
# @input: grid-3d
# @empty-cells: yes
# @complexities:
#   boxMax: log(X)*log(Y)*log(Z)
#   boxSum: log(X)*log(Y)*log(Z)
#   maxAll: 1
#   maxGteGteGte: log(X)*log(Y)*log(Z)
#   maxLteLteLte: log(X)*log(Y)*log(Z)
#   pointAdd: log(X)*log(Y)*log(Z)
#   pointAssign: log(X)*log(Y)*log(Z)
#   pointChmax: log(X)*log(Y)*log(Z)
#   pointChmin: log(X)*log(Y)*log(Z)
#   pointGet: 1
#   sumAll: 1
#   sumGteGteGte: log(X)*log(Y)*log(Z)
#   sumLteLteLte: log(X)*log(Y)*log(Z)
#   build: X*Y*Z
# @memory:
#   layout: 2n-iterative
#   node: sm[8*X*Y*Z] mx[8*X*Y*Z]
#   tags: none
#   other: none
#   note: one flat array per aggregate, 2X x-nodes by 2Y y-nodes by 2Z z-nodes

NEG = float("-inf")  # an empty cell in the max array


# 3D segment tree (sum, max): point updates and any-box queries on an X x Y x Z grid, O(log X * log Y * log Z) each. A
# bottom-up tree over x whose every node is a tree over y whose every node is a tree over z, in one flat array per
# aggregate (8 * X * Y * Z entries each, so the three sides have to be small: compress coordinates first). Coordinates
# are 0-based and boxes are inclusive: x1..x2, y1..y2, z1..z2. Every cell starts empty and queries only see set cells:
# a min / max over no set cell is None; a sum over none is 0.
class SegTree3D:
    __slots__ = ("X", "Y", "Z", "SY", "SZ", "sm", "mx")

    # O(X*Y*Z) -- X by Y by Z, every cell empty; needs X >= 1, Y >= 1 and Z >= 1, else ValueError
    def __init__(self, X, Y, Z):
        if X < 1 or Y < 1 or Z < 1:
            raise ValueError(f"SegTree3D: needs X >= 1, Y >= 1 and Z >= 1, got X = {X}, Y = {Y}, Z = {Z}")
        self.X = X
        self.Y = Y
        self.Z = Z
        self.SY = 2 * Y  # y-nodes per x-node
        self.SZ = 2 * Z  # z-nodes per y-node
        self.sm = [0] * (8 * X * Y * Z)
        self.mx = [NEG] * (8 * X * Y * Z)

    # cell (x, y, z) = v, then every node above it
    def _set(self, x, y, z, v):
        X, Y, Z, SY, SZ = self.X, self.Y, self.Z, self.SY, self.SZ
        sm, mx = self.sm, self.mx
        px = x + X
        py = y + Y
        base = (px * SY + py) * SZ  # the cell's own z-tree
        sm[base + z + Z] = v
        mx[base + z + Z] = v
        pz = (z + Z) >> 1
        while pz:
            sm[base + pz] = sm[base + 2 * pz] + sm[base + 2 * pz + 1]
            lhs = mx[base + 2 * pz]
            rhs = mx[base + 2 * pz + 1]
            mx[base + pz] = lhs if lhs > rhs else rhs
            pz >>= 1
        py >>= 1
        while py:  # the y-nodes above, still in the cell's own x
            base = (px * SY + py) * SZ
            lo = (px * SY + 2 * py) * SZ
            hi = lo + SZ
            pz = z + Z
            while pz:
                sm[base + pz] = sm[lo + pz] + sm[hi + pz]
                lhs = mx[lo + pz]
                rhs = mx[hi + pz]
                mx[base + pz] = lhs if lhs > rhs else rhs
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
                    lhs = mx[lo + pz]
                    rhs = mx[hi + pz]
                    mx[base + pz] = lhs if lhs > rhs else rhs
                    pz >>= 1
                py >>= 1
            px >>= 1

    # O(1) -- the value at (x, y, z), None if the cell is empty; needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else
    # IndexError
    def pointGet(self, x, y, z):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointGet: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        cur = self.mx[((x + self.X) * self.SY + y + self.Y) * self.SZ + z + self.Z]
        return None if cur == NEG else cur

    # O(log X * log Y * log Z) -- the cell at (x, y, z) becomes v (it may go down as well as up); needs 0 <= x < X, 0 <=
    # y < Y and 0 <= z < Z, else IndexError
    def pointAssign(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointAssign: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        self._set(x, y, z, v)

    # O(log X * log Y * log Z) -- adds v to the cell at (x, y, z); an empty cell becomes v; needs 0 <= x < X, 0 <= y < Y
    # and 0 <= z < Z, else IndexError
    def pointAdd(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointAdd: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        cur = self.mx[((x + self.X) * self.SY + y + self.Y) * self.SZ + z + self.Z]
        self._set(x, y, z, v if cur == NEG else cur + v)

    # O(log X * log Y * log Z) -- the cell at (x, y, z) becomes max(itself, v); an empty cell becomes v; needs 0 <= x <
    # X, 0 <= y < Y and 0 <= z < Z, else IndexError
    def pointChmax(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointChmax: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        cur = self.mx[((x + self.X) * self.SY + y + self.Y) * self.SZ + z + self.Z]
        if cur == NEG or v > cur:
            self._set(x, y, z, v)

    # O(log X * log Y * log Z) -- the cell at (x, y, z) becomes min(itself, v); an empty cell becomes v; needs 0 <= x <
    # X, 0 <= y < Y and 0 <= z < Z, else IndexError
    def pointChmin(self, x, y, z, v):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"pointChmin: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        cur = self.mx[((x + self.X) * self.SY + y + self.Y) * self.SZ + z + self.Z]
        if cur == NEG or v < cur:
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

    # O(log X * log Y * log Z) -- sum of the set cells in the box x1..x2, y1..y2, z1..z2 (0 if there are none); needs 0
    # <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, else IndexError
    def boxSum(self, x1, y1, z1, x2, y2, z2):
        if not (0 <= x1 <= x2 < self.X and 0 <= y1 <= y2 < self.Y and 0 <= z1 <= z2 < self.Z):
            raise IndexError(f"boxSum: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, "
                             f"got x1 = {x1}, y1 = {y1}, z1 = {z1}, x2 = {x2}, y2 = {y2}, z2 = {z2}, X = {self.X}, "
                             f"Y = {self.Y}, Z = {self.Z}")
        return self._sumOf(x1, y1, z1, x2, y2, z2)

    # O(1) -- sum of every set cell (0 if there are none)
    def sumAll(self):
        return self.sm[(self.SY + 1) * self.SZ + 1]

    # O(log X * log Y * log Z) -- sum of the cells with all three coordinates <= x, y, z; needs 0 <= x < X, 0 <= y < Y
    # and 0 <= z < Z, else IndexError
    def sumLteLteLte(self, x, y, z):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"sumLteLteLte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        return self._sumOf(0, 0, 0, x, y, z)

    # O(log X * log Y * log Z) -- sum of the cells with all three coordinates >= x, y, z; needs 0 <= x < X, 0 <= y < Y
    # and 0 <= z < Z, else IndexError
    def sumGteGteGte(self, x, y, z):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"sumGteGteGte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        return self._sumOf(x, y, z, self.X - 1, self.Y - 1, self.Z - 1)

    def _maxOf(self, x1, y1, z1, x2, y2, z2):
        X, Y, Z, SY, SZ = self.X, self.Y, self.Z, self.SY, self.SZ
        mx = self.mx
        res = NEG
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
                                cand = mx[base + lz]
                                if cand > res:
                                    res = cand
                                lz += 1
                            if rz & 1:
                                rz -= 1
                                cand = mx[base + rz]
                                if cand > res:
                                    res = cand
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
                                cand = mx[base + lz]
                                if cand > res:
                                    res = cand
                                lz += 1
                            if rz & 1:
                                rz -= 1
                                cand = mx[base + rz]
                                if cand > res:
                                    res = cand
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
                                cand = mx[base + lz]
                                if cand > res:
                                    res = cand
                                lz += 1
                            if rz & 1:
                                rz -= 1
                                cand = mx[base + rz]
                                if cand > res:
                                    res = cand
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
                                cand = mx[base + lz]
                                if cand > res:
                                    res = cand
                                lz += 1
                            if rz & 1:
                                rz -= 1
                                cand = mx[base + rz]
                                if cand > res:
                                    res = cand
                            lz >>= 1
                            rz >>= 1
                    ly >>= 1
                    ry >>= 1
            lx >>= 1
            rx >>= 1
        return None if res == NEG else res

    # O(log X * log Y * log Z) -- max of the set cells in the box x1..x2, y1..y2, z1..z2 (None if there are none); needs
    # 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, else IndexError
    def boxMax(self, x1, y1, z1, x2, y2, z2):
        if not (0 <= x1 <= x2 < self.X and 0 <= y1 <= y2 < self.Y and 0 <= z1 <= z2 < self.Z):
            raise IndexError(f"boxMax: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, "
                             f"got x1 = {x1}, y1 = {y1}, z1 = {z1}, x2 = {x2}, y2 = {y2}, z2 = {z2}, X = {self.X}, "
                             f"Y = {self.Y}, Z = {self.Z}")
        return self._maxOf(x1, y1, z1, x2, y2, z2)

    # O(1) -- max of every set cell (None if there are none)
    def maxAll(self):
        res = self.mx[(self.SY + 1) * self.SZ + 1]
        return None if res == NEG else res

    # O(log X * log Y * log Z) -- max of the set cells with all three coordinates <= x, y, z (None if there are none);
    # needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else IndexError
    def maxLteLteLte(self, x, y, z):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"maxLteLteLte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        return self._maxOf(0, 0, 0, x, y, z)

    # O(log X * log Y * log Z) -- max of the set cells with all three coordinates >= x, y, z (None if there are none);
    # needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else IndexError
    def maxGteGteGte(self, x, y, z):
        if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):
            raise IndexError(f"maxGteGteGte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {x}, y = {y}, "
                             f"z = {z}, X = {self.X}, Y = {self.Y}, Z = {self.Z}")
        return self._maxOf(x, y, z, self.X - 1, self.Y - 1, self.Z - 1)
