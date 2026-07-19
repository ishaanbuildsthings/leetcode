class Solution:
    def maxTrailingZeros(self, grid: List[List[int]]) -> int:

        h = len(grid)
        w = len(grid[0])
        mapped = [[[0, 0] for _ in range(w)] for _ in range(h)] # mapped[r][c] -> [num 2s, num 5s]
        for r in range(h):
            for c in range(w):
                curr = grid[r][c]
                while curr % 2 == 0:
                    mapped[r][c][0] += 1
                    curr //= 2
                while curr % 5 == 0:
                    mapped[r][c][1] += 1
                    curr //= 5
    
        # if we extend out from here to the edge, how many 2s and 5s do we get
        @cache
        def dp(r, c, dir):
            if r == h or r == -1 or c == w or c == -1:
                return [0, 0]
            
            here = mapped[r][c]
            nxt = dp(r + dir[0], c + dir[1], dir)
            return [here[0] + nxt[0], here[1] + nxt[1]]
        
        res = 0

        DIRS = [(1,0),(-1,0),(0,1),(0,-1)]

        for r in range(h):
            for c in range(w):
                # treat this as the corner point
                for i in range(len(DIRS)):
                    dir1 = DIRS[i]
                    gain1 = dp(r, c, dir1)
                    for j in range(i + 1, len(DIRS)):
                        dir2 = DIRS[j]
                        gain2 = dp(r, c, dir2)

                        finalGain = [gain1[0] + gain2[0], gain1[1] + gain2[1]]
                        finalGain[0] -= mapped[r][c][0]
                        finalGain[1] -= mapped[r][c][1]

                        res = max(res, min(finalGain))
        
        return res
                        