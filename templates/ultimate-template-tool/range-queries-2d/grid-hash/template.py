# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-hash/template.py
# @operations: hashAll rectHash rectsEqual
# @data-structure-type: hash
# @input: grid
# @complexities:
#   hashAll: 1
#   rectHash: 1
#   rectsEqual: 1
#   build: R*C
# @memory:
#   layout: none
#   node: pre[1*R*C]
#   tags: none
#   other: powR[1*R] powC[1*C]
#   note: pre is (R + 1) by (C + 1), flat: the hash of the rows above r and the columns left of c

import random

_HP = (1 << 61) - 1  # hashes are mod this prime
_HA = random.randrange(1 << 40, _HP - 1)  # the base down the rows, picked at random each run
_HB = random.randrange(1 << 40, _HP - 1)  # the base along the columns
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0


# 2D hashing of a board (the 1D polynomial hash with one base per direction): the hash of any rectangle in O(1), and
# equal rectangles hash equal wherever they sit, so two rectangles of the same size can be compared in O(1). A cell
# (i, j) of a rectangle counts as value * A^(rows below it) * B^(columns right of it), mod the prime 2^61 - 1; the
# prefix table then gives a rectangle from four entries, each shifted by a power of A and B. Both bases and a value
# offset are picked at random each run, so no test can be built against them. Cells can be numbers or single
# characters. No updates. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.
class Hash2D:
    __slots__ = ("R", "C", "W", "pre", "powR", "powC")

    # O(R*C) -- grid: R rows of C cells each (numbers or single characters; a list of strings works); needs R >= 1
    # and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("Hash2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = C + 1
        P, A, B = _HP, _HA, _HB
        powR = self.powR = [1] * (R + 1)
        for i in range(R):
            powR[i + 1] = powR[i] * A % P
        powC = self.powC = [1] * (C + 1)
        for j in range(C):
            powC[j + 1] = powC[j] * B % P
        pre = self.pre = [0] * ((R + 1) * W)
        for r in range(R):
            row = grid[r]
            up = r * W
            at = up + W
            run = 0  # this row alone, left to right
            for c in range(C):
                v = row[c]
                run = (run * B + (ord(v) if isinstance(v, str) else v) + _HO) % P
                pre[at + c + 1] = (pre[up + c + 1] * A + run) % P

    def _hashOf(self, r1, c1, r2, c2):
        pre, W, P = self.pre, self.W, _HP
        a = self.powR[r2 - r1 + 1]
        b = self.powC[c2 - c1 + 1]
        top = r1 * W
        bot = (r2 + 1) * W
        return (pre[bot + c2 + 1] - pre[top + c2 + 1] * a - pre[bot + c1] * b + pre[top + c1] * a % P * b) % P

    # O(1) -- hash of rows r1..r2, columns c1..c2: rectangles with equal cells hash equal; needs 0 <= r1 <= r2 < R and 0
    # <= c1 <= c2 < C, else IndexError
    def rectHash(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectHash: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._hashOf(r1, c1, r2, c2)

    # O(1) -- is the rectangle rows r1..r2, columns c1..c2 equal, cell by cell, to the same-size rectangle whose
    # top-left
    # cell is (r3, c3); needs both inside the grid, else IndexError
    def rectsEqual(self, r1, c1, r2, c2, r3, c3):
        r4 = r3 + r2 - r1
        c4 = c3 + c2 - c1
        ok = 0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C
        if not (ok and 0 <= r3 and r4 < self.R and 0 <= c3 and c4 < self.C):
            raise IndexError(f"rectsEqual: needs both rectangles inside the grid, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, r3 = {r3}, c3 = {c3}, R = {self.R}, C = {self.C}")
        return self._hashOf(r1, c1, r2, c2) == self._hashOf(r3, c3, r4, c4)

    # O(1) -- hash of the whole grid
    def hashAll(self):
        return self.pre[-1]
