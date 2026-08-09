class Solution:
    def maxIncreasingCells(self, mat: List[List[int]]) -> int:
        height = len(mat)
        width = len(mat[0])

        cells = [] # holds (val, r, c)
        for r in range(height):
            for c in range(width):
                cells.append((mat[r][c], r, c))

        groups = defaultdict(list) # maps val -> list of coords
        for val, r, c in cells:
            groups[val].append((r, c))
        
        allVals = sorted(set([cell[0] for cell in cells]))

        rowMax = [0] * height
        colMax = [0] * width

        for uniqVal in allVals:
            rowUpdates = {}
            colUpdates = {}
            for r, c in groups[uniqVal]:
                prevRow = rowMax[r]
                prevCol = colMax[c]
                best = 1 + max(prevRow, prevCol)
                rowUpdates[r] = max(rowUpdates.get(r, 0), best)
                colUpdates[c] = max(colUpdates.get(c, 0), best)
            for row, update in rowUpdates.items():
                rowMax[row] = max(rowMax[row], update)
            for col, update in colUpdates.items():
                colMax[col] = max(colMax[col], update)
        
        return max(rowMax)

        