class Solution:
    def numEnclaves(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        seen = set() # so we don't duplicate islands

        diffs = [[1,0], [-1,0], [0,1], [0,-1] ]

        # dfs tells us if some child cell touched an edge, and the total number of cells we have in our island
        def dfs(r, c):
            seen.add(r * WIDTH + c)

            sizeForThis = 1
            hasTouchedLandForThis = False

            for rowDiff, colDiff in diffs:
                newRow = rowDiff + r
                newCol = colDiff + c
                # skip out of bounds
                if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                    hasTouchedLandForThis = True
                    continue
                # skip water
                if grid[newRow][newCol] == 0:
                    continue
                # skip seen land
                if newRow * WIDTH + newCol in seen:
                    continue
                sizeForAdj, hasTouchedLandForAdj = dfs(newRow, newCol)
                sizeForThis += sizeForAdj
                hasTouchedLandForThis = hasTouchedLandForThis or hasTouchedLandForAdj
            return [sizeForThis, hasTouchedLandForThis]
        res = 0
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if grid[r][c] == 0:
                    continue
                if r * WIDTH + c in seen:
                    continue
                sizeOfIsland, canTouchLand = dfs(r, c)
                if not canTouchLand:
                    res += sizeOfIsland
        return res

