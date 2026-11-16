# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-window-max/template.py
# @operations: windowMax
# @data-structure-type: sliding-window
# @input: grid
# @complexities:
#   windowMax: 1
#   build: R*C
# @memory:
#   layout: none
#   node: mx[1*R*C]
#   tags: none
#   other: none
#   note: one answer per window position, (R - h + 1) by (C - w + 1); the build also uses one R by (C - w + 1) scratch table



# The max of every h x w window of a grid, for one window size fixed at the build: O(R * C) to build with no log (a
# sliding-window max along each row with a monotonic queue, then the same down each column of those), then O(1) per
# window. When every query has the same size this beats a sparse table on build time and memory. No updates. Rows and
# columns are 0-based; a window is named by its top-left cell.
class WindowMax2D:
    __slots__ = ("R", "C", "h", "w", "outW", "mx")

    # O(R*C) -- grid: R rows of C numbers each; windows are h rows by w columns; needs 1 <= h <= R and 1 <= w <= C, else
    # ValueError
    def __init__(self, grid, h, w):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("WindowMax2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        if not (1 <= h <= R and 1 <= w <= C):
            raise ValueError(f"WindowMax2D: needs 1 <= h <= R and 1 <= w <= C, got h = {h}, w = {w}, R = {R}, "
                             f"C = {C}")
        self.h = h
        self.w = w
        outW = self.outW = C - w + 1
        rows = []  # rows[r][c]: the max of grid[r][c .. c + w - 1]
        for row in grid:
            out = []
            q = [0] * C  # column indices, their values falling
            head = tail = 0
            for c in range(C):
                v = row[c]
                while tail > head and row[q[tail - 1]] <= v:
                    tail -= 1
                q[tail] = c
                tail += 1
                if q[head] <= c - w:
                    head += 1
                if c >= w - 1:
                    out.append(row[q[head]])
            rows.append(out)
        res = self.mx = [0] * ((R - h + 1) * outW)
        q = [0] * R
        for c in range(outW):
            head = tail = 0
            for r in range(R):
                v = rows[r][c]
                while tail > head and rows[q[tail - 1]][c] <= v:
                    tail -= 1
                q[tail] = r
                tail += 1
                if q[head] <= r - h:
                    head += 1
                if r >= h - 1:
                    res[(r - h + 1) * outW + c] = rows[q[head]][c]

    # O(1) -- max of the h x w window whose top-left cell is (r, c); needs 0 <= r <= R - h and 0 <= c <= C - w, else
    # IndexError
    def windowMax(self, r, c):
        if not (0 <= r <= self.R - self.h and 0 <= c <= self.C - self.w):
            raise IndexError(f"windowMax: needs 0 <= r <= R - h and 0 <= c <= C - w, got r = {r}, c = {c}, "
                             f"R = {self.R}, C = {self.C}, h = {self.h}, w = {self.w}")
        return self.mx[r * self.outW + c]
