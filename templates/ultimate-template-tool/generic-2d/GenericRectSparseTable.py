# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-2d/GenericRectSparseTable.py

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


# A static R x C grid (no updates): O(R*C*logR*logC) build and Nodes of memory, O(1) rectQuery (at most 3 combine
# calls). For square queries only, GenericSquareSparseTable needs a single log.
# st = RectSparseTable(grid, baseFn, combine)    # grid: a list of R rows, each a list of C values
class RectSparseTable:
    def __init__(self, grid, baseFn, combine):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("RectSparseTable: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        self.combine = combine
        levelsR, levelsC = R.bit_length(), C.bit_length()
        # t[kr][kc]: the Node of every window of 2^kr rows by 2^kc columns, flat, (R - 2^kr + 1) rows of (C - 2^kc + 1)
        t = self.t = [[None] * levelsC for _ in range(levelsR)]
        t[0][0] = [baseFn(v, r, c) for r, row in enumerate(grid) for c, v in enumerate(row)]
        for kc in range(1, levelsC):
            half = 1 << (kc - 1)
            prevW = C - half + 1
            prev, cur = t[0][kc - 1], []
            for r in range(R):
                seg = prev[r * prevW:(r + 1) * prevW]
                cur += [combine(x, y) for x, y in zip(seg, seg[half:])]
            t[0][kc] = cur
        for kr in range(1, levelsR):
            half = 1 << (kr - 1)
            for kc in range(levelsC):
                prev = t[kr - 1][kc]
                off = half * (C - (1 << kc) + 1)
                t[kr][kc] = [combine(x, y) for x, y in zip(prev, prev[off:])]

    # the Node of cell (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError("pointGet: needs 0 <= r < R and 0 <= c < C")
        return self.t[0][0][r * self.C + c]

    # the Node of rows r1..r2, columns c1..c2: the combine of four power-of-two windows, one in each corner (they
    # overlap, which is why combine must be idempotent); needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectQuery(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError("rectQuery: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C")
        kr = (r2 - r1 + 1).bit_length() - 1
        kc = (c2 - c1 + 1).bit_length() - 1
        t = self.t[kr][kc]
        w = self.C - (1 << kc) + 1
        i = r1 * w + c1
        j = (r2 - (1 << kr) + 1) * w + c1
        d = c2 - (1 << kc) + 1 - c1
        top = self.combine(t[i], t[i + d]) if d else t[i]
        if i == j:
            return top
        return self.combine(top, self.combine(t[j], t[j + d]) if d else t[j])

    # the Node of the whole grid
    def rectQueryAll(self):
        return self.rectQuery(0, 0, self.R - 1, self.C - 1)
