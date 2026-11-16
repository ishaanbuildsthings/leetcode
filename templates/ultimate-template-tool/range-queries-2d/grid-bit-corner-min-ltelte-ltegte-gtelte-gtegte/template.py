# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-corner-min-ltelte-ltegte-gtelte-gtegte/template.py
# @operations: minAll minGteGte minGteLte minLteGte minLteLte pointChmin
# @data-structure-type: BIT
# @input: grid
# @empty-cells: yes
# @complexities:
#   minAll: 1
#   minGteGte: log(R)*log(C)
#   minGteLte: log(R)*log(C)
#   minLteGte: log(R)*log(C)
#   minLteLte: log(R)*log(C)
#   pointChmin: log(R)*log(C)
#   build: R*C
# @memory:
#   layout: none
#   node: tLteLte[1*R*C] tLteGte[1*R*C] tGteLte[1*R*C] tGteGte[1*R*C]
#   tags: none
#   other: none
#   note: one Fenwick tree per corner direction, each (R + 1) by (C + 1), flat; a >= direction is the same tree with that axis mirrored

POS = float("inf")  # an empty cell


# Corner min with a 2D Fenwick tree: pointChmin at a cell and the min over a corner of the grid (every cell with row
# <= r or >= r, and column <= c or >= c), O(log R * log C) each, with a quarter of a 2D segment tree's memory per
# direction and a much smaller constant. This works because values only move one way: a cell can only go down
# (pointChmin), so a tree entry never has to forget a value. For a cell that can move both ways, or for rectangles
# that aren't corners, use the 2D segment tree. A cell can be empty and queries only see set cells. Rows and columns
# are 0-based. An empty cell is None in the grid, and a min over no set cell is None.
class CornerMinFenwick2D:
    __slots__ = ("R", "C", "W", "best", "tLteLte", "tLteGte", "tGteLte", "tGteGte")

    # O(R*C) -- grid: R rows of C values each (None = an empty cell); needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("CornerMinFenwick2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = C + 1
        best = POS
        t = self.tLteLte = [POS] * ((R + 1) * W)
        for r in range(R):
            at = (r + 1) * W
            row = grid[r]
            for c in range(C):
                v = row[c]
                if v is not None:
                    t[at + c + 1] = v
                    if v < best:
                        best = v
        for i in range(1, R + 1):
            at = i * W
            for j in range(1, C + 1):  # each entry is folded into the next one that covers it
                p = j + (j & -j)
                if p <= C and t[at + j] < t[at + p]:
                    t[at + p] = t[at + j]
        for i in range(1, R + 1):
            p = i + (i & -i)
            if p <= R:
                a = i * W
                b = p * W
                for j in range(1, C + 1):
                    if t[a + j] < t[b + j]:
                        t[b + j] = t[a + j]
        t = self.tLteGte = [POS] * ((R + 1) * W)
        for r in range(R):
            at = (r + 1) * W
            row = grid[r]
            for c in range(C):
                v = row[c]
                if v is not None:
                    t[at + C - c] = v
                    if v < best:
                        best = v
        for i in range(1, R + 1):
            at = i * W
            for j in range(1, C + 1):  # each entry is folded into the next one that covers it
                p = j + (j & -j)
                if p <= C and t[at + j] < t[at + p]:
                    t[at + p] = t[at + j]
        for i in range(1, R + 1):
            p = i + (i & -i)
            if p <= R:
                a = i * W
                b = p * W
                for j in range(1, C + 1):
                    if t[a + j] < t[b + j]:
                        t[b + j] = t[a + j]
        t = self.tGteLte = [POS] * ((R + 1) * W)
        for r in range(R):
            at = (R - r) * W
            row = grid[r]
            for c in range(C):
                v = row[c]
                if v is not None:
                    t[at + c + 1] = v
                    if v < best:
                        best = v
        for i in range(1, R + 1):
            at = i * W
            for j in range(1, C + 1):  # each entry is folded into the next one that covers it
                p = j + (j & -j)
                if p <= C and t[at + j] < t[at + p]:
                    t[at + p] = t[at + j]
        for i in range(1, R + 1):
            p = i + (i & -i)
            if p <= R:
                a = i * W
                b = p * W
                for j in range(1, C + 1):
                    if t[a + j] < t[b + j]:
                        t[b + j] = t[a + j]
        t = self.tGteGte = [POS] * ((R + 1) * W)
        for r in range(R):
            at = (R - r) * W
            row = grid[r]
            for c in range(C):
                v = row[c]
                if v is not None:
                    t[at + C - c] = v
                    if v < best:
                        best = v
        for i in range(1, R + 1):
            at = i * W
            for j in range(1, C + 1):  # each entry is folded into the next one that covers it
                p = j + (j & -j)
                if p <= C and t[at + j] < t[at + p]:
                    t[at + p] = t[at + j]
        for i in range(1, R + 1):
            p = i + (i & -i)
            if p <= R:
                a = i * W
                b = p * W
                for j in range(1, C + 1):
                    if t[a + j] < t[b + j]:
                        t[b + j] = t[a + j]
        self.best = best

    # O(log R * log C) -- the cell at (r, c) becomes min(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    # <= c
    # < C, else IndexError
    def pointChmin(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmin: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        R, C, W = self.R, self.C, self.W
        if v < self.best:
            self.best = v
        t = self.tLteLte
        i = r + 1
        cj = c + 1
        while i <= R:
            base = i * W
            j = cj
            while j <= C:
                if v < t[base + j]:
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
                if v < t[base + j]:
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
                if v < t[base + j]:
                    t[base + j] = v
                j += j & -j
            i += i & -i
        t = self.tGteGte
        i = R - r
        cj = C - c
        while i <= R:
            base = i * W
            j = cj
            while j <= C:
                if v < t[base + j]:
                    t[base + j] = v
                j += j & -j
            i += i & -i

    # O(log R * log C) -- min of the set cells with row <= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def minLteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minLteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        W, t, res = self.W, self.tLteLte, POS
        i = r + 1
        cj = c + 1
        while i > 0:
            base = i * W
            j = cj
            while j > 0:
                x = t[base + j]
                if x < res:
                    res = x
                j &= j - 1
            i &= i - 1
        return None if res == POS else res

    # O(log R * log C) -- min of the set cells with row <= r and column >= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def minLteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minLteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        W, t, res = self.W, self.tLteGte, POS
        i = r + 1
        cj = self.C - c
        while i > 0:
            base = i * W
            j = cj
            while j > 0:
                x = t[base + j]
                if x < res:
                    res = x
                j &= j - 1
            i &= i - 1
        return None if res == POS else res

    # O(log R * log C) -- min of the set cells with row >= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def minGteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minGteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        W, t, res = self.W, self.tGteLte, POS
        i = self.R - r
        cj = c + 1
        while i > 0:
            base = i * W
            j = cj
            while j > 0:
                x = t[base + j]
                if x < res:
                    res = x
                j &= j - 1
            i &= i - 1
        return None if res == POS else res

    # O(log R * log C) -- min of the set cells with row >= r and column >= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def minGteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minGteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        W, t, res = self.W, self.tGteGte, POS
        i = self.R - r
        cj = self.C - c
        while i > 0:
            base = i * W
            j = cj
            while j > 0:
                x = t[base + j]
                if x < res:
                    res = x
                j &= j - 1
            i &= i - 1
        return None if res == POS else res

    # O(1) -- min of every set cell (None if there are none)
    def minAll(self):
        return None if self.best == POS else self.best
