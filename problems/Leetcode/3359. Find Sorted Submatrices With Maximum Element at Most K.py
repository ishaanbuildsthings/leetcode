class Solution:
    def countSubmatrices(self, grid: List[List[int]], k: int) -> int:
        h1 = len(grid)
        w1 = len(grid[0])
        rotated = [[None for _ in range(h1)] for _ in range(w1)]
        for r in range(h1):
            for c in range(w1):
                nc = r
                nr = w1 - c - 1
                rotated[nr][nc] = grid[r][c]
        
        height = len(rotated)
        width = len(rotated[0])
        
        upChain = [[0 for _ in range(width)] for _ in range(height)]
        for r in range(height):
            for c in range(width):
                if rotated[r][c] > k:
                    continue
                if r == 0:
                    upChain[r][c] = 1
                    continue
                above = rotated[r-1][c]
                canUse = above <= k and above <= rotated[r][c]
                upChain[r][c] = (1 + upChain[r-1][c]) if canUse else 1
        
        def solveForHist(hist):
            n = len(hist)
            nearestLeftLte = [-1] * n
            nearestRightLt = [n] * n

            # strictly increasing stack
            stack = []
            for i in range(n - 1, -1, -1):
                v = hist[i]
                while stack and v <= hist[stack[-1]]:
                    poppedI = stack.pop()
                    nearestLeftLte[poppedI] = i
                stack.append(i)
            
            # mono increasing stack
            stack = []
            for i, v in enumerate(hist):
                while stack and v < hist[stack[-1]]:
                    poppedI = stack.pop()
                    nearestRightLt[poppedI] = i
                stack.append(i)
            
            res = 0

            for i, v in enumerate(hist):
                reachLeft = nearestLeftLte[i] + 1
                reachRight = nearestRightLt[i] - 1
                leftOpts = i - reachLeft + 1
                rightOpts = reachRight - i + 1
                opts = leftOpts * rightOpts * v
                res += opts
            
            return res
        
        ans = 0
        for row in upChain:
            ans += solveForHist(row)
        
        return ans



