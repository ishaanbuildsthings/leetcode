# TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
from collections import defaultdict

class SparseBIT2DRangeUpdateRangeSum:
    """
    Sparse 2D Binary Indexed Tree supporting:
      - range add: add v to every cell in [x1, x2] x [y1, y2]
      - range sum query: sum over [x1, x2] x [y1, y2]

    Uses the four-BIT coefficient decomposition. Backed by dicts so
    coordinates can be arbitrary integers in [loX, hiX] x [loY, hiY]
    without allocating O(u^2) memory. Accepts negative coordinates;
    shifts are handled internally.

    Complexities are in terms of u = universe size (coordinate range),
    not the number of operations performed.
    """

    # O(1)
    def __init__(self, loX, hiX, loY, hiY):
        self.offX = 1 - loX  # maps loX -> 1
        self.offY = 1 - loY  # maps loY -> 1
        self.u = max(hiX + self.offX, hiY + self.offY) + 1
        # Four BITs storing coefficients for the decomposition:
        # prefix_sum(X, Y) = sum_{x<=X, y<=Y} (
        #     T1[x][y] * X * Y
        #   - T2[x][y] * Y
        #   - T3[x][y] * X
        #   + T4[x][y]
        # )
        self.t1 = defaultdict(lambda: defaultdict(int))
        self.t2 = defaultdict(lambda: defaultdict(int))
        self.t3 = defaultdict(lambda: defaultdict(int))
        self.t4 = defaultdict(lambda: defaultdict(int))

    # O(log^2 u) — point update on all four BITs
    def _updatePoint(self, x, y, v):
        vx, vy, vxy = v * x, v * y, v * x * y
        i = x
        while i <= self.u:
            row1, row2, row3, row4 = self.t1[i], self.t2[i], self.t3[i], self.t4[i]
            j = y
            while j <= self.u:
                row1[j] += v
                row2[j] += vx
                row3[j] += vy
                row4[j] += vxy
                j += j & -j
            i += i & -i

    # O(log^2 u) — prefix sum over [1, x] x [1, y]
    def _queryPrefix(self, x, y):
        total = 0
        i = x
        while i > 0:
            row1, row2, row3, row4 = self.t1[i], self.t2[i], self.t3[i], self.t4[i]
            j = y
            while j > 0:
                total += row1[j] * (x + 1) * (y + 1) \
                       - row2[j] * (y + 1) \
                       - row3[j] * (x + 1) \
                       + row4[j]
                j -= j & -j
            i -= i & -i
        return total

    # O(log^2 u) — add v to every cell in [x1, x2] x [y1, y2] (inclusive)
    def rangeAdd(self, x1, y1, x2, y2, v):
        x1 += self.offX; x2 += self.offX
        y1 += self.offY; y2 += self.offY
        self._updatePoint(x1,     y1,     v)
        self._updatePoint(x1,     y2 + 1, -v)
        self._updatePoint(x2 + 1, y1,     -v)
        self._updatePoint(x2 + 1, y2 + 1, v)

    # O(log^2 u) — sum over [x1, x2] x [y1, y2] (inclusive)
    def rangeSum(self, x1, y1, x2, y2):
        x1 += self.offX; x2 += self.offX
        y1 += self.offY; y2 += self.offY
        return (
              self._queryPrefix(x2,     y2)
            - self._queryPrefix(x1 - 1, y2)
            - self._queryPrefix(x2,     y1 - 1)
            + self._queryPrefix(x1 - 1, y1 - 1)
        )