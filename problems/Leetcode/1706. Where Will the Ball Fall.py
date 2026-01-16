class Solution:
    def findBall(self, grid: List[List[int]]) -> List[int]:
        height = len(grid)
        width = len(grid[0])

        @cache
        def dfs(r, c, pos, movesAtThisRow):
            if c < 0 or c == width:
                return -1
            if movesAtThisRow == 3:
                return -1 # V shape. this was the fastest way to implement
            if r == height:
                return c
            if grid[r][c] == 1:
                if pos == 'up':
                    return dfs(r, c + 1, 'left', movesAtThisRow + 1)
                if pos == 'down':
                    return dfs(r + 1, c, 'up', 1)
                if pos == 'right':
                    return dfs(r, c + 1, 'left', movesAtThisRow + 1)
                if pos == 'left':
                    return dfs(r + 1, c, 'up', 1)
            if pos == 'up':
                return dfs(r, c - 1, 'right', movesAtThisRow + 1)
            if pos == 'down':
                return dfs(r + 1, c, 'up', 1)
            if pos == 'left':
                return dfs(r, c - 1, 'right', movesAtThisRow + 1)
            return dfs(r + 1, c, 'up', 1)
        
        res = []
        for i in range(width):
            res.append(dfs(0, i, 'up', 1))
        return res
