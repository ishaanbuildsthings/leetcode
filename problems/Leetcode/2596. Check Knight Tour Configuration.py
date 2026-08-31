class Solution:
    def checkValidGrid(self, grid: List[List[int]]) -> bool:
        # better than 8n^2 is to collect coordinates for everything, and then look up every number and see if the diff is valid
        height = len(grid)
        width = len(grid[0])

        DIFFS = [ [2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2] ]
        def getValidAdj(r, c, num):
            for rowDiff, colDiff in DIFFS:
                newRow = r + rowDiff
                newCol = c + colDiff
                if newRow >= 0 and newRow < height and newCol >= 0 and newCol < width and grid[newRow][newCol] == num + 1:
                    return (newRow, newCol)
            return False

        if grid[0][0]:
            return False

        r = c = num = 0
        while num != width * height - 1:
            nextResult = getValidAdj(r, c, num)
            if nextResult == False:
                return False
            else:
                r, c = nextResult
            num += 1
        
        return True
            