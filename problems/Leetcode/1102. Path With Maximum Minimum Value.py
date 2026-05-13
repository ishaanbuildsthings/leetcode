# can reduce from n*m*log k to n*m*log(n*m) by only binary searching on the array of possible k values, so generate that array first and sort it then iterate on that
class Solution:
    def maximumMinimumPath(self, grid: List[List[int]]) -> int:
        height = len(grid)
        width = len(grid[0])

        # find if a score of x is viable
        def canTraverseWithMinVal(x):
            DIFFS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]
            seen = {(0, 0)}
            q = collections.deque()
            q.append((0, 0))
            if grid[0][0] < x:
                return False
            while q:
                length = len(q)
                for _ in range(length):
                    r, c = q.popleft()
                    for rowDiff, colDiff in DIFFS:
                        newRow = rowDiff + r
                        newCol = colDiff + c
                        # reach the end
                        if newRow == height - 1 and newCol == width - 1:
                            return grid[newRow][newCol] >= x
                        # skip out of bounds
                        if newRow < 0 or newRow == height or newCol < 0 or newCol == width:
                            continue
                        # skip seen
                        if (newRow, newCol) in seen:
                            continue
                        # skip too small ones
                        if grid[newRow][newCol] < x:
                            continue
                        seen.add((newRow, newCol))
                        q.append((newRow,newCol))
            return False

        l = 0
        r = max(max(row) for row in grid)
        while l < r:
            m = math.ceil((r + l) / 2)
            if canTraverseWithMinVal(m):
                l = m
            else:
                r = m - 1
        return l
        
