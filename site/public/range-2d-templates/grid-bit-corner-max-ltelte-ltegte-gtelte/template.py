# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-corner-max-ltelte-ltegte-gtelte/template.py
# @operations: maxAll maxGteLte maxLteGte maxLteLte pointChmax
# @data-structure-type: BIT
# @input: grid
# @empty-cells: yes
# @complexities:
#   maxAll: 1
#   maxGteLte: log(R)*log(C)
#   maxLteGte: log(R)*log(C)
#   maxLteLte: log(R)*log(C)
#   pointChmax: log(R)*log(C)
#   build: R*C
# @memory:
#   layout: none
#   node: tLteLte[1*R*C] tLteGte[1*R*C] tGteLte[1*R*C]
#   tags: none
#   other: none
#   note: one Fenwick tree per corner direction, each (R + 1) by (C + 1), flat; a >= direction is the same tree with that axis mirrored

NEG = float("-inf")  # an empty cell


# Corner max with a 2D Fenwick tree: pointChmax at a cell and the max over a corner of the grid (every cell with row
# <= r or >= r, and column <= c or >= c), O(log R * log C) each, with a quarter of a 2D segment tree's memory per
# direction and a much smaller constant. This works because values only move one way: a cell can only go up
# (pointChmax), so a tree entry never has to forget a value. For a cell that can move both ways, or for rectangles
# that aren't corners, use the 2D segment tree. A cell can be empty and queries only see set cells. Rows and columns
# are 0-based. An empty cell is None in the grid, and a max over no set cell is None.
class CornerMaxFenwick2D:
    __slots__ = ("R", "C", "W", "best", "tLteLte", "tLteGte", "tGteLte")

    # O(R*C) -- grid: R rows of C values each (None = an empty cell); needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("CornerMaxFenwick2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = C + 1
        best = NEG
        t = self.tLteLte = [NEG] * ((R + 1) * W)
        for r in range(R):
            at = (r + 1) * W
            row = grid[r]
            for c in range(C):
                v = row[c]
                if v is not None:
                    t[at + c + 1] = v
                    if v > best:
                        best = v
        for i in range(1, R + 1):
            at = i * W
            for j in range(1, C + 1):  # each entry is folded into the next one that covers it
                p = j + (j & -j)
                if p <= C and t[at + j] > t[at + p]:
                    t[at + p] = t[at + j]
        for i in range(1, R + 1):
            p = i + (i & -i)
            if p <= R:
                a = i * W
                b = p * W
                for j in range(1, C + 1):
                    if t[a + j] > t[b + j]:
                        t[b + j] = t[a + j]
        t = self.tLteGte = [NEG] * ((R + 1) * W)
        for r in range(R):
            at = (r + 1) * W
            row = grid[r]
            for c in range(C):
                v = row[c]
                if v is not None:
                    t[at + C - c] = v
                    if v > best:
                        best = v
        for i in range(1, R + 1):
            at = i * W
            for j in range(1, C + 1):  # each entry is folded into the next one that covers it
                p = j + (j & -j)
                if p <= C and t[at + j] > t[at + p]:
                    t[at + p] = t[at + j]
        for i in range(1, R + 1):
            p = i + (i & -i)
            if p <= R:
                a = i * W
                b = p * W
                for j in range(1, C + 1):
                    if t[a + j] > t[b + j]:
                        t[b + j] = t[a + j]
        t = self.tGteLte = [NEG] * ((R + 1) * W)
        for r in range(R):
            at = (R - r) * W
            row = grid[r]
            for c in range(C):
                v = row[c]
                if v is not None:
                    t[at + c + 1] = v
                    if v > best:
                        best = v
        for i in range(1, R + 1):
            at = i * W
            for j in range(1, C + 1):  # each entry is folded into the next one that covers it
                p = j + (j & -j)
                if p <= C and t[at + j] > t[at + p]:
                    t[at + p] = t[at + j]
        for i in range(1, R + 1):
            p = i + (i & -i)
            if p <= R:
                a = i * W
                b = p * W
                for j in range(1, C + 1):
                    if t[a + j] > t[b + j]:
                        t[b + j] = t[a + j]
        self.best = best

    # O(log R * log C) -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    # <= c < C, else IndexError
    def pointChmax(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmax: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        R, C, W = self.R, self.C, self.W
        if v > self.best:
            self.best = v
        t = self.tLteLte
        i = r + 1
        cj = c + 1
        while i <= R:
            base = i * W
            j = cj
            while j <= C:
                if v > t[base + j]:
                    t[base + j] = v
                j += j & -j
            i += i & -i
        t = self.tLteGte
        i = r + 1
        cj = C - c
        while i <= R:
            base = i * W
            j = cj
            while j <= C:
                if v > t[base + j]:
                    t[base + j] = v
                j += j & -j
            i += i & -i
        t = self.tGteLte
        i = R - r
        cj = c + 1
        while i <= R:
            base = i * W
            j = cj
            while j <= C:
                if v > t[base + j]:
                    t[base + j] = v
                j += j & -j
            i += i & -i

    # O(log R * log C) -- max of the set cells with row <= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxLteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxLteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        W, t, res = self.W, self.tLteLte, NEG
        i = r + 1
        cj = c + 1
        while i > 0:
            base = i * W
            j = cj
            while j > 0:
                x = t[base + j]
                if x > res:
                    res = x
                j &= j - 1
            i &= i - 1
        return None if res == NEG else res

    # O(log R * log C) -- max of the set cells with row <= r and column >= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxLteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxLteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        W, t, res = self.W, self.tLteGte, NEG
        i = r + 1
        cj = self.C - c
        while i > 0:
            base = i * W
            j = cj
            while j > 0:
                x = t[base + j]
                if x > res:
                    res = x
                j &= j - 1
            i &= i - 1
        return None if res == NEG else res

    # O(log R * log C) -- max of the set cells with row >= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxGteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxGteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        W, t, res = self.W, self.tGteLte, NEG
        i = self.R - r
        cj = c + 1
        while i > 0:
            base = i * W
            j = cj
            while j > 0:
                x = t[base + j]
                if x > res:
                    res = x
                j &= j - 1
            i &= i - 1
        return None if res == NEG else res

    # O(1) -- max of every set cell (None if there are none)
    def maxAll(self):
        return None if self.best == NEG else self.best
