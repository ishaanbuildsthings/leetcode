# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-square-sparse-table-max-gcd-and-or/template.py
# @operations: pointGet squareAnd squareGcd squareMax squareOr
# @data-structure-type: square-sparse-table
# @input: grid
# @complexities:
#   pointGet: 1
#   squareAnd: 1
#   squareGcd: log(U) ?
#   squareMax: 1
#   squareOr: 1
#   build: R*C*log(min(R,C))*log(U) ?
# @memory:
#   layout: none
#   node: mx[1*R*C*log(min(R,C))] gc[1*R*C*log(min(R,C))] an[1*R*C*log(min(R,C))] orr[1*R*C*log(min(R,C))]
#   tags: none
#   other: none
#   note: per aggregate, one table per power-of-two side (side 1 is the grid itself, shared)

from math import gcd



# Static sparse table for square queries only (max, gcd, AND, OR): O(1) per square (one gcd run, O(log U)), with a
# single log of memory and build, R * C * log(min(R, C)), where the any-rectangle sparse table needs log R * log C.
# Level k holds the aggregate of every 2^k by 2^k window; a square is covered by four such windows, one in each corner
# (they overlap, which is fine for these aggregates). No updates. Rows and columns are 0-based; a square is its
# top-left cell (r, c) and its side.
class SquareSparseTable2D:
    __slots__ = ("R", "C", "mx", "gc", "an", "orr")

    # O(R*C*log(min(R, C))*logU) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("SquareSparseTable2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        flat = [v for row in grid for v in row]
        levels = min(R, C).bit_length()
        t = self.mx = [flat]  # t[k]: windows of 2^k by 2^k, flat, (R - 2^k + 1) rows of (C - 2^k + 1)
        for k in range(1, levels):
            half = 1 << (k - 1)
            prevW = C - half + 1
            prev = t[-1]
            cur = []
            for i in range(R - (1 << k) + 1):
                top = prev[i * prevW:(i + 1) * prevW]
                bot = prev[(i + half) * prevW:(i + half + 1) * prevW]
                cur += [max(w, x, y, z) for w, x, y, z in zip(top, top[half:], bot, bot[half:])]
            t.append(cur)
        t = self.gc = [flat]  # t[k]: windows of 2^k by 2^k, flat, (R - 2^k + 1) rows of (C - 2^k + 1)
        for k in range(1, levels):
            half = 1 << (k - 1)
            prevW = C - half + 1
            prev = t[-1]
            cur = []
            for i in range(R - (1 << k) + 1):
                top = prev[i * prevW:(i + 1) * prevW]
                bot = prev[(i + half) * prevW:(i + half + 1) * prevW]
                cur += [gcd(w, x, y, z) for w, x, y, z in zip(top, top[half:], bot, bot[half:])]
            t.append(cur)
        t = self.an = [flat]  # t[k]: windows of 2^k by 2^k, flat, (R - 2^k + 1) rows of (C - 2^k + 1)
        for k in range(1, levels):
            half = 1 << (k - 1)
            prevW = C - half + 1
            prev = t[-1]
            cur = []
            for i in range(R - (1 << k) + 1):
                top = prev[i * prevW:(i + 1) * prevW]
                bot = prev[(i + half) * prevW:(i + half + 1) * prevW]
                cur += [w & x & y & z for w, x, y, z in zip(top, top[half:], bot, bot[half:])]
            t.append(cur)
        t = self.orr = [flat]  # t[k]: windows of 2^k by 2^k, flat, (R - 2^k + 1) rows of (C - 2^k + 1)
        for k in range(1, levels):
            half = 1 << (k - 1)
            prevW = C - half + 1
            prev = t[-1]
            cur = []
            for i in range(R - (1 << k) + 1):
                top = prev[i * prevW:(i + 1) * prevW]
                bot = prev[(i + half) * prevW:(i + half + 1) * prevW]
                cur += [w | x | y | z for w, x, y, z in zip(top, top[half:], bot, bot[half:])]
            t.append(cur)

    # O(1) -- max of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the square
    # inside the grid, else IndexError
    def squareMax(self, r, c, side):
        if not (side >= 1 and 0 <= r and r + side <= self.R and 0 <= c and c + side <= self.C):
            raise IndexError(f"squareMax: needs side >= 1 and the square inside the grid, got r = {r}, c = {c}, "
                             f"side = {side}, R = {self.R}, C = {self.C}")
        k = side.bit_length() - 1
        t = self.mx[k]
        w = self.C - (1 << k) + 1
        d = side - (1 << k)
        i = r * w + c
        j = i + d * w
        return max(t[i], t[i + d], t[j], t[j + d])

    # O(log U) -- gcd of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the
    # square inside the grid, else IndexError
    def squareGcd(self, r, c, side):
        if not (side >= 1 and 0 <= r and r + side <= self.R and 0 <= c and c + side <= self.C):
            raise IndexError(f"squareGcd: needs side >= 1 and the square inside the grid, got r = {r}, c = {c}, "
                             f"side = {side}, R = {self.R}, C = {self.C}")
        k = side.bit_length() - 1
        t = self.gc[k]
        w = self.C - (1 << k) + 1
        d = side - (1 << k)
        i = r * w + c
        j = i + d * w
        return gcd(t[i], t[i + d], t[j], t[j + d])

    # O(1) -- AND of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the square
    # inside the grid, else IndexError
    def squareAnd(self, r, c, side):
        if not (side >= 1 and 0 <= r and r + side <= self.R and 0 <= c and c + side <= self.C):
            raise IndexError(f"squareAnd: needs side >= 1 and the square inside the grid, got r = {r}, c = {c}, "
                             f"side = {side}, R = {self.R}, C = {self.C}")
        k = side.bit_length() - 1
        t = self.an[k]
        w = self.C - (1 << k) + 1
        d = side - (1 << k)
        i = r * w + c
        j = i + d * w
        return t[i] & t[i + d] & t[j] & t[j + d]

    # O(1) -- OR of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the square
    # inside the grid, else IndexError
    def squareOr(self, r, c, side):
        if not (side >= 1 and 0 <= r and r + side <= self.R and 0 <= c and c + side <= self.C):
            raise IndexError(f"squareOr: needs side >= 1 and the square inside the grid, got r = {r}, c = {c}, "
                             f"side = {side}, R = {self.R}, C = {self.C}")
        k = side.bit_length() - 1
        t = self.orr[k]
        w = self.C - (1 << k) + 1
        d = side - (1 << k)
        i = r * w + c
        j = i + d * w
        return t[i] | t[i + d] | t[j] | t[j + d]

    # O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.mx[0][r * self.C + c]
