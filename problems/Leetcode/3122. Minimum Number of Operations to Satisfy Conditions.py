class Solution:
    def minimumOperations(self, grid: List[List[int]]) -> int:

        # SOLUTION 1, normal dp(colI, prevNum) and we loop through 10 options
        # H = len(grid)
        # W = len(grid[0])

        # # colCounts[colI][numType] -> count of numType in that column
        # colCounts = [[0] * 10 for _ in range(W)]
        # for c in range(W):
        #     for num in range(10):
        #         amt = 0
        #         for r in range(H):
        #             if grid[r][c] == num:
        #                 amt += 1
        #         colCounts[c][num] = amt

        # @cache
        # def dp(colI, prev):
        #     if colI == W:
        #         return 0
        #     res = inf
        #     for num in range(10):
        #         if num == prev:
        #             continue
        #         amt = colCounts[colI][num]
        #         changes = H - amt
        #         score = changes + dp(colI + 1, num)
        #         res = min(res, score)
        #     return res

        # return min(dp(0, x) for x in range(10))



        # SOLUTION 2, have up to 3 options in each?? don't actually know if this is valid or if test cases are weak
        # H = len(grid)
        # W = len(grid[0])

        # # colCounts[colI][numType] -> count of numType in that column
        # colCounts = [[0] * 10 for _ in range(W)]
        # for c in range(W):
        #     for num in range(10):
        #         amt = 0
        #         for r in range(H):
        #             if grid[r][c] == num:
        #                 amt += 1
        #         colCounts[c][num] = amt

        # colTop3 = []
        # for c in range(W):
        #     costs = sorted((H - colCounts[c][num], num) for num in range(10))
        #     colTop3.append([costs[0], costs[1], costs[2]])

        # @cache
        # def dp(colI, prev):
        #     if colI == W:
        #         return 0
        #     res = inf
        #     for cost, num in colTop3[colI]:
        #         if num == prev:
        #             continue
        #         res = min(res, cost + dp(colI + 1, num))
        #     return res

        # return dp(0, -1)






        # SOLTUION 3, best + second-best trick where we stuff things into the return value
        H = len(grid)
        W = len(grid[0])

        # colCounts[colI][numType] -> count of numType in that column
        colCounts = [[0] * 10 for _ in range(W)]
        for c in range(W):
            for num in range(10):
                amt = 0
                for r in range(H):
                    if grid[r][c] == num:
                        amt += 1
                colCounts[c][num] = amt
        
        @cache
        def dp(i):
            if i == W:
                return (0, -1), (0, -2) # returns best score, value used in this column. -1 and -2 are sentinels
            
            (nxtBest1, nxtUsed1), (nxtBest2, nxtUsed2) = dp(i + 1)
            options = []
            for v in range(10):
                payment = H - colCounts[i][v]
                if v == nxtUsed1:
                    totalCost = payment + nxtBest2
                else:
                    totalCost = payment + nxtBest1
                options.append((totalCost, v))
            options.sort()

            best1, bestUsed1 = options[0]
            best2, bestUsed2 = options[1]
            return (best1, bestUsed1), (best2, bestUsed2)
        
        return dp(0)[0][0]







