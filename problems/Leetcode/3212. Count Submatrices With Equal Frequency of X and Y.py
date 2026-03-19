class Solution:
    def numberOfSubmatrices(self, grid: List[List[str]]) -> int:
        
        # count of X
        prefixSums = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]
        pfY = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                # X
                sumForCell = 0
                if r > 0:
                    sumForCell += prefixSums[r - 1][c]
                if c > 0:
                    sumForCell += prefixSums[r][c - 1]
                sumForCell += (grid[r][c] == 'X')
                if r > 0 and c > 0:
                    sumForCell -= prefixSums[r-1][c-1]
                prefixSums[r][c] = sumForCell
                
                
                # y
                sumY = 0
                if r > 0:
                    sumY += pfY[r-1][c]
                if c > 0:
                    sumY += pfY[r][c-1]
                sumY += grid[r][c] == 'Y'
                if r and c:
                    sumY -= pfY[r-1][c-1]
                pfY[r][c]=sumY
        
        def query(row1, col1, row2, col2):
            sumForRegion = 0
            sumForRegion += prefixSums[row2][col2]
            if row1 > 0 and col1 > 0:
                sumForRegion += prefixSums[row1 - 1][col1 - 1]
            if col1 > 0:
                sumForRegion -= prefixSums[row2][col1 - 1]
            if row1 > 0:
                sumForRegion -= prefixSums[row1 - 1][col2]
            return sumForRegion
        
        def qY(r1, c1, r2, c2):
            sumY = 0
            sumY += pfY[r2][c2]
            if r1 and c1:
                sumY += pfY[r1-1][c1-1]
            if c1:
                sumY -= pfY[r2][c1-1]
            if r1:
                sumY -= pfY[r-1][c2]
            return sumY
        
        res = 0
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                # print(f'r:{r} c: {c}')
                totX = query(0, 0, r, c)
                totY = qY(0, 0, r, c)
                # print(f'totX: {totX} totY: {totY}')
                res += (totX == totY) and totX > 0
        return res

        