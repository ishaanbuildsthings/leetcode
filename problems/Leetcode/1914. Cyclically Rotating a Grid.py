class Solution:
    def rotateGrid(self, grid: List[List[int]], k: int) -> List[List[int]]:

        # solution 1, O(n * m) clean
        h = len(grid)
        w = len(grid[0])
        res = [[0] * w for _ in range(h)]
        for L in range(min(h,w)//2):
            layerHeight = h - (2 * L)
            layerWidth = w - (2 * L)
            cells = []
            for c in range(L, L + layerWidth):
                cells.append((L, c))
            for r in range(L + 1, L + layerHeight):
                cells.append((r, w - L - 1))
            for c in range(L + layerWidth - 2, L - 1, -1):
                cells.append((L + layerHeight - 1, c))
            for r in range(L + layerHeight - 2, L, -1):
                cells.append((r, L))
            vals = [grid[r][c] for r, c in cells]
            for i in range(len(cells)):
                shifted = (i + k) % len(cells)
                nval = vals[shifted]
                r, c = cells[i]
                res[r][c] = nval
        return res

        # solution 2, O(n * m * (n + m)) dp where for each cell we take k % border and step ahead that many times
        # height = len(grid)
        # width = len(grid[0])
        # numLayers = min(height, width) // 2
        # res = [row[:] for row in grid]

        # @cache
        # def dp(r, c, dirTup, layer, rem):
        #     if rem == 0:
        #         return grid[r][c]
        #     r1, c1 = layer, layer
        #     r2, c2 = height - 1 - layer, width - 1 - layer
        #     dr, dc = dirTup
        #     nr, nc = r + dr, c + dc
        #     if r1 <= nr <= r2 and c1 <= nc <= c2:
        #         return dp(nr, nc, dirTup, layer, rem - 1)
        #     ndr, ndc = dc, -dr
        #     return dp(r + ndr, c + ndc, (ndr, ndc), layer, rem - 1)

        # def getDir(r, c, layer):
        #     r1, c1 = layer, layer
        #     r2, c2 = height - 1 - layer, width - 1 - layer
        #     if r == r1 and c < c2: return (0, 1)
        #     if c == c2 and r < r2: return (1, 0)
        #     if r == r2 and c > c1: return (0, -1)
        #     return (-1, 0)

        # for layer in range(numLayers):
        #     r1, c1 = layer, layer
        #     r2, c2 = height - 1 - layer, width - 1 - layer
        #     perim = 2 * (r2 - r1 + c2 - c1)
        #     rem = k % perim
        #     for r in range(r1, r2 + 1):
        #         for c in range(c1, c2 + 1):
        #             if r == r1 or r == r2 or c == c1 or c == c2:
        #                 res[r][c] = dp(r, c, getDir(r, c, layer), layer, rem)

        # return res