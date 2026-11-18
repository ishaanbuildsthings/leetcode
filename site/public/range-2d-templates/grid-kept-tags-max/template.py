# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-kept-tags-max/template.py
# @operations: maxAll maxGteGte maxGteLte maxLteGte maxLteLte pointChmax pointGet rectChmax rectMax
# @data-structure-type: seg-tree-kept-tags
# @input: grid
# @empty-cells: yes
# @complexities:
#   maxAll: 1
#   maxGteGte: log(R)*log(C)
#   maxGteLte: log(R)*log(C)
#   maxLteGte: log(R)*log(C)
#   maxLteLte: log(R)*log(C)
#   pointChmax: log(R)*log(C)
#   pointGet: log(R)*log(C)
#   rectChmax: log(R)*log(C)
#   rectMax: log(R)*log(C)
#   build: R*C
# @memory:
#   layout: 2n-iterative
#   node: fullBest[4*R*C] partBest[4*R*C]
#   tags: fullTag[4*R*C] partTag[4*R*C]
#   other: none
#   note: per row-node two column trees (updates covering all of its rows; updates touching any of its rows), each a tag array and a best-below array, 2R row-nodes by 2C column-nodes, flat

NEG = float("-inf")  # an empty cell


# Rectangle chmax and rectangle max on an R x C grid, O(log R * log C) each: a 2D segment tree whose tags stay where
# they are put (no push-down, which a tree of trees can't do). rectChmax(r1, c1, r2, c2, v) makes every cell of the
# rectangle max(itself, v). Every row-node keeps two column trees: one for the updates that cover all of its rows, and
# one for the updates that touch any of its rows. A query takes, from the row-nodes that make up its rows, the second
# kind, and from the row-nodes above those, the first kind (an update covering a whole row-node above covers the
# query's rows too). Each column tree works the same way one level down. This only works because chmax never has to be
# undone: there is no rectangle assign or add here. A cell can be empty and queries only see set cells. Rows and
# columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. An empty cell is None in the grid,
# and a max over no set cell is None.
class RectChmaxRectMax2D:
    __slots__ = ("R", "C", "W", "best", "fullTag", "fullBest", "partTag", "partBest")

    # O(R*C) -- grid: R rows of C values each (None = an empty cell); needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("RectChmaxRectMax2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = 2 * C
        self.fullTag = [NEG] * (2 * R * W)
        self.partTag = [NEG] * (2 * R * W)
        full = self.fullBest = [NEG] * (2 * R * W)
        best = NEG
        for r in range(R):
            base = (r + R) * W
            i = base + C
            for v in grid[r]:
                if v is not None:
                    full[i] = v
                    if v > best:
                        best = v
                i += 1
            for pc in range(C - 1, 0, -1):
                x = full[base + 2 * pc]
                y = full[base + 2 * pc + 1]
                full[base + pc] = x if x > y else y
        part = self.partBest = full[:]  # a single row: the two trees agree
        for pr in range(R - 1, 0, -1):
            base = pr * W
            lo = 2 * base
            hi = lo + W
            for pc in range(1, W):
                x = part[lo + pc]
                y = part[hi + pc]
                part[base + pc] = x if x > y else y
        self.best = best

    # one column tree (the one starting at `base`): columns c1..c2 become max(themselves, v)
    def _colsUpdate(self, tag, best, base, c1, c2, v):
        C = self.C
        lc = c1 + C
        rc = c2 + C + 1
        a = lc >> 1  # every node above the two ends has v somewhere below it now
        b = (rc - 1) >> 1
        while a or b:
            if a and v > best[base + a]:
                best[base + a] = v
            if b and v > best[base + b]:
                best[base + b] = v
            a >>= 1
            b >>= 1
        while lc < rc:
            if lc & 1:
                if v > tag[base + lc]:
                    tag[base + lc] = v
                    if v > best[base + lc]:
                        best[base + lc] = v
                lc += 1
            if rc & 1:
                rc -= 1
                if v > tag[base + rc]:
                    tag[base + rc] = v
                    if v > best[base + rc]:
                        best[base + rc] = v
            lc >>= 1
            rc >>= 1

    # one column tree: the max over columns c1..c2
    def _colsQuery(self, tag, best, base, c1, c2):
        C = self.C
        lc = c1 + C
        rc = c2 + C + 1
        res = NEG
        a = lc >> 1  # a tag on a node above either end covers that end, which is inside c1..c2
        b = (rc - 1) >> 1
        while a or b:
            if a:
                x = tag[base + a]
                if x > res:
                    res = x
            if b:
                x = tag[base + b]
                if x > res:
                    res = x
            a >>= 1
            b >>= 1
        while lc < rc:
            if lc & 1:
                x = best[base + lc]
                if x > res:
                    res = x
                lc += 1
            if rc & 1:
                rc -= 1
                x = best[base + rc]
                if x > res:
                    res = x
            lc >>= 1
            rc >>= 1
        return res

    def _update(self, r1, c1, r2, c2, v):
        R, W = self.R, self.W
        fullTag, fullBest, partTag, partBest = self.fullTag, self.fullBest, self.partTag, self.partBest
        cols = self._colsUpdate
        if v > self.best:
            self.best = v
        lr = r1 + R
        rr = r2 + R + 1
        a = lr >> 1  # every row-node above the two ends is touched
        b = (rr - 1) >> 1
        while a or b:
            if a:
                cols(partTag, partBest, a * W, c1, c2, v)
            if b and b != a:
                cols(partTag, partBest, b * W, c1, c2, v)
            a >>= 1
            b >>= 1
        while lr < rr:
            if lr & 1:
                cols(fullTag, fullBest, lr * W, c1, c2, v)
                cols(partTag, partBest, lr * W, c1, c2, v)
                lr += 1
            if rr & 1:
                rr -= 1
                cols(fullTag, fullBest, rr * W, c1, c2, v)
                cols(partTag, partBest, rr * W, c1, c2, v)
            lr >>= 1
            rr >>= 1

    def _query(self, r1, c1, r2, c2):
        R, W = self.R, self.W
        fullTag, fullBest, partTag, partBest = self.fullTag, self.fullBest, self.partTag, self.partBest
        cols = self._colsQuery
        res = NEG
        lr = r1 + R
        rr = r2 + R + 1
        a = lr >> 1  # an update covering a whole row-node above either end covers that end's row
        b = (rr - 1) >> 1
        while a or b:
            if a:
                x = cols(fullTag, fullBest, a * W, c1, c2)
                if x > res:
                    res = x
            if b and b != a:
                x = cols(fullTag, fullBest, b * W, c1, c2)
                if x > res:
                    res = x
            a >>= 1
            b >>= 1
        while lr < rr:
            if lr & 1:
                x = cols(partTag, partBest, lr * W, c1, c2)
                if x > res:
                    res = x
                lr += 1
            if rr & 1:
                rr -= 1
                x = cols(partTag, partBest, rr * W, c1, c2)
                if x > res:
                    res = x
            lr >>= 1
            rr >>= 1
        return None if res == NEG else res

    # O(log R * log C) -- every cell of rows r1..r2, columns c1..c2 becomes max(itself, v); an empty cell becomes v;
    # needs
    # 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectChmax(self, r1, c1, r2, c2, v):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectChmax: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        self._update(r1, c1, r2, c2, v)

    # O(log R * log C) -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    # <= c < C, else IndexError
    def pointChmax(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmax: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        self._update(r, c, r, c, v)

    # O(log R * log C) -- the value at (r, c), None if the cell is empty; needs 0 <= r < R and 0 <= c < C, else
    # IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._query(r, c, r, c)

    # O(log R * log C) -- max of the set cells in rows r1..r2, columns c1..c2 (None if there are none); needs 0 <= r1 <=
    # r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectMax(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectMax: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._query(r1, c1, r2, c2)

    # O(log R * log C) -- max of the set cells with row <= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxLteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxLteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._query(0, 0, r, c)

    # O(log R * log C) -- max of the set cells with row <= r and column >= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxLteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxLteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._query(0, c, r, self.C - 1)

    # O(log R * log C) -- max of the set cells with row >= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxGteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxGteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._query(r, 0, self.R - 1, c)

    # O(log R * log C) -- max of the set cells with row >= r and column >= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxGteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxGteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._query(r, c, self.R - 1, self.C - 1)

    # O(1) -- max of every set cell (None if there are none)
    def maxAll(self):
        return None if self.best == NEG else self.best
