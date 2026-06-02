class Solution:
    def floodFill(self, image: List[List[int]], sr: int, sc: int, color: int) -> List[List[int]]:
        seen = set()

        def dfs(r, c):
            seen.add((r, c))
            for rowDiff, colDiff in [[1,0],[-1,0],[0,1],[0,-1]]:
                nr, nc = r+rowDiff, c+colDiff
                if nr<0 or nr == len(image) or nc < 0 or nc == len(image[0]):
                    continue
                if (nr,nc) in seen:
                    continue
                if image[nr][nc] != image[sr][sc]:
                    continue
                dfs(nr,nc)
        dfs(sr,sc)
        for r,c in seen:
            image[r][c] = color
        return image