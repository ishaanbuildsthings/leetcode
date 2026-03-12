class Solution:
    def countIslands(self, grid: List[List[int]], k: int) -> int:
        res = 0
        seen = set()

        def dfs(r, c, currArr):
            seen.add((r,c))
            currArr[0] += grid[r][c]
            for rd, cd in [[1,0],[-1,0],[0,1],[0,-1]]:
                nr,nc = r+rd,c+cd
                if (nr,nc) in seen:
                    continue
                if nr<0 or nc<0 or nr==len(grid) or nc==len(grid[0]):
                    continue
                if grid[nr][nc] == 0:
                    continue
                dfs(nr,nc,currArr)

        res = 0
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if (r, c) in seen:
                    continue
                if grid[r][c] == 0:
                    continue
                arr = [0]
                dfs(r, c, arr)
                if arr[0] % k == 0:
                    res += 1

        return res
            
            