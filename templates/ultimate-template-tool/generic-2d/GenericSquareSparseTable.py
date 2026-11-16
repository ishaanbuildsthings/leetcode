# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-2d/GenericSquareSparseTable.py

# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


def baseFn(v: RawVal, r: int, c: int) -> Node:
    # return (v, v)
    pass


# combine MUST be idempotent: combine(x, x) == x (min, max, gcd, lcm, AND, OR, ... but NOT sum or count), and the
# order of its two arguments must not matter
def combine(a: Node, b: Node) -> Node:
    # return (min(a[0], b[0]), max(a[1], b[1]))
    pass


# A static R x C grid (no updates), square queries only: O(R*C*log(min(R, C))) build and Nodes of memory (a single
# log, where GenericRectSparseTable needs log R * log C), O(1) squareQuery (at most 3 combine calls).
# st = SquareSparseTable(grid, baseFn, combine)    # grid: a list of R rows, each a list of C values
class SquareSparseTable:
    def __init__(self, grid, baseFn, combine):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("SquareSparseTable: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        self.combine = combine
        # t[k]: the Node of every 2^k by 2^k window, flat, (R - 2^k + 1) rows of (C - 2^k + 1)
        t = self.t = [[baseFn(v, r, c) for r, row in enumerate(grid) for c, v in enumerate(row)]]
        for k in range(1, min(R, C).bit_length()):
            half = 1 << (k - 1)
            prevW = C - half + 1
            prev, cur = t[-1], []
            for i in range(R - (1 << k) + 1):
                top = prev[i * prevW:(i + 1) * prevW]
                bot = prev[(i + half) * prevW:(i + half + 1) * prevW]
                cur += [combine(combine(w, x), combine(y, z)) for w, x, y, z in zip(top, top[half:], bot, bot[half:])]
            t.append(cur)

    # the Node of cell (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError("pointGet: needs 0 <= r < R and 0 <= c < C")
        return self.t[0][r * self.C + c]

    # the Node of the square with top-left cell (r, c) and that many rows and columns: the combine of four power-of-two
    # squares, one in each corner (they overlap, which is why combine must be idempotent); needs side >= 1 and the
    # square inside the grid, else IndexError
    def squareQuery(self, r, c, side):
        if not (side >= 1 and 0 <= r and r + side <= self.R and 0 <= c and c + side <= self.C):
            raise IndexError("squareQuery: needs side >= 1 and the square inside the grid")
        k = side.bit_length() - 1
        t = self.t[k]
        w = self.C - (1 << k) + 1
        d = side - (1 << k)
        i = r * w + c
        if not d:
            return t[i]
        j = i + d * w
        return self.combine(self.combine(t[i], t[i + d]), self.combine(t[j], t[j + d]))
