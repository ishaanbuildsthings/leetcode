# TEMPLATE FROM MY GITHUB: ishaanbuildsthings
# O(n*m * log(min(n, m))) build time
class SquareSparseTable:
    def __init__(self, grid, combine):
        self.combine = combine
        h = len(grid)
        w = len(grid[0])
        LOG = min(h, w).bit_length()
        
        self.dp = [None] * LOG
        self.dp[0] = [row[:] for row in grid]
        
        for p in range(1, LOG):
            side = 1 << p
            half = side >> 1
            rows = h - side + 1
            cols = w - side + 1
            if rows <= 0 or cols <= 0:
                break
            self.dp[p] = [[0] * cols for _ in range(rows)]
            for r in range(rows):
                for c in range(cols):
                    self.dp[p][r][c] = combine(
                        combine(self.dp[p-1][r][c], self.dp[p-1][r+half][c]),
                        combine(self.dp[p-1][r][c+half], self.dp[p-1][r+half][c+half])
                    )
    
    # Query a square with top-left (r1, c1) and side length sideLen
    def query(self, r1, c1, sideLen):
        bit = sideLen.bit_length() - 1
        offset = sideLen - (1 << bit)
        return self.combine(
            self.combine(
                self.dp[bit][r1][c1],
                self.dp[bit][r1+offset][c1]
            ),
            self.combine(
                self.dp[bit][r1][c1+offset],
                self.dp[bit][r1+offset][c1+offset]
            )
        )

# Usage:
# grid = [[1,2,3],[4,5,6],[7,8,9]]
# st = SquareSparseTable(grid, lambda a, b: max(a, b))
# print(st.query(0, 0, 2))  # max of top-left 2x2 = max([[1,2],[4,5]]) = 5