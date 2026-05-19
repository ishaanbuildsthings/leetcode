# TEMPLATE FROM MY GITHUB: ishaanbuildsthings
# O(n * m * logN * logM) build time
class RectangleSparseTable:
    def __init__(self, grid, combine):
        self.combine = combine
        h = len(grid)
        w = len(grid[0])
        LOG_H = h.bit_length()  # if h=10, this is 4
        LOG_W = w.bit_length()
        self.LOG_H = LOG_H
        self.LOG_W = LOG_W
        
        # dp[powH][powW][r][c] = combine over rectangle of size 2^powH x 2^powW starting at (r, c)
        self.dp = [[None] * LOG_W for _ in range(LOG_H)]
        
        # Base: powH = 0, powW = 0 → 1x1 = the grid itself
        self.dp[0][0] = [row[:] for row in grid]
        
        # Build powH = 0, powW > 0 (rows of doubling width)
        for pw in range(1, LOG_W):
            width = 1 << pw
            halfW = width >> 1
            cols = w - width + 1
            if cols <= 0:
                break
            self.dp[0][pw] = [[0] * cols for _ in range(h)]
            for r in range(h):
                for c in range(cols):
                    self.dp[0][pw][r][c] = combine(self.dp[0][pw-1][r][c], self.dp[0][pw-1][r][c+halfW])
        
        # Build powH > 0, powW = 0 (cols of doubling height)
        for ph in range(1, LOG_H):
            height = 1 << ph
            halfH = height >> 1
            rows = h - height + 1
            if rows <= 0:
                break
            self.dp[ph][0] = [[0] * w for _ in range(rows)]
            for r in range(rows):
                for c in range(w):
                    self.dp[ph][0][r][c] = combine(self.dp[ph-1][0][r][c], self.dp[ph-1][0][r+halfH][c])
        
        # Build powH > 0, powW > 0
        for ph in range(1, LOG_H):
            height = 1 << ph
            halfH = height >> 1
            rows = h - height + 1
            if rows <= 0:
                continue
            for pw in range(1, LOG_W):
                width = 1 << pw
                halfW = width >> 1
                cols = w - width + 1
                if cols <= 0:
                    continue
                self.dp[ph][pw] = [[0] * cols for _ in range(rows)]
                for r in range(rows):
                    for c in range(cols):
                        self.dp[ph][pw][r][c] = combine(
                            combine(self.dp[ph-1][pw-1][r][c], self.dp[ph-1][pw-1][r+halfH][c]),
                            combine(self.dp[ph-1][pw-1][r][c+halfW], self.dp[ph-1][pw-1][r+halfH][c+halfW])
                        )
    
    # Query the rectangle [r1..r2] x [c1..c2] (inclusive)
    def query(self, r1, r2, c1, c2):
        height = r2 - r1 + 1
        width = c2 - c1 + 1
        heightBit = height.bit_length() - 1  # __lg equivalent
        widthBit = width.bit_length() - 1
        heightOffset = height - (1 << heightBit)
        widthOffset = width - (1 << widthBit)
        return self.combine(
            self.combine(
                self.dp[heightBit][widthBit][r1][c1],
                self.dp[heightBit][widthBit][r1+heightOffset][c1]
            ),
            self.combine(
                self.dp[heightBit][widthBit][r1][c1+widthOffset],
                self.dp[heightBit][widthBit][r1+heightOffset][c1+widthOffset]
            )
        )


# Usage:
# grid = [[1,2,3],[4,5,6],[7,8,9]]
# st = RectangleSparseTable(grid, lambda a, b: max(a, b))
# print(st.query(0, 1, 0, 2))  # max of [[1,2,3],[4,5,6]] = 6