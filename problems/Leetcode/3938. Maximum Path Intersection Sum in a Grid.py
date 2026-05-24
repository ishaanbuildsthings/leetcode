def pp(mat):
    for row in mat:
        print(row)
        
class Solution:
    def maxScore(self, grid: List[List[int]]) -> int:
        res = -inf

        # pp(grid)

        # kadanes with subarray at min size 2
        # def fn(arr):
        #     mx1 = -inf # max prefix with at least 1, ending right before us
        #     res = -inf
        #     for v in arr:
        #         nmx1 = max(v, mx1 + v)
        #         res = max(res, v + mx1)
        #         mx1 = nmx1

        #     return res
    
        # top down kadanes with subarray at min size 2
        def fn(arr):
            resHere = -inf
            @cache
            def dp(i, state, size2):
                if i == len(arr):
                    if size2:
                        return 0
                    return -inf
                
                if state == 0:
                    ifSkip = dp(i + 1, 0, 0)
                    ifStart = arr[i] + dp(i + 1, 1, 0)
                    return max(ifSkip, ifStart)
                if state == 1:
                    if size2:
                        ifEnd = 0
                        ifCont = arr[i] + dp(i + 1, 1, 1)
                        return max(ifEnd, ifCont)
                    ifCont = arr[i] + dp(i + 1, 1, 1)
                    return ifCont
        
            return dp(0, 0, 0)
                    

                

        for row in grid:
            ans = fn(row[::])
            res = max(res, ans)

        W = len(grid[0])
        H = len(grid)
        for c in range(W):
            col = []
            for r in range(len(grid)):
                col.append(grid[r][c])
            ans = fn(col)
            res = max(res, ans)

        for r in range(1, H - 1):
            for c in range(1, W - 1):
                res = max(res, grid[r][c])

        return res
            