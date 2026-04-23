class Solution:
    def maxPathScore(self, grid: List[List[int]], k: int) -> int:

        # SOLUTION 0, postfix cost (meaning already including the current cell)
        costMap = {
            0 : 0,
            1 : 1,
            2 : 1
        }

        h = len(grid)
        w = len(grid[0])

        @cache
        def dp(r, c, postfixCost):
            if postfixCost > k:
                return -inf
            if r == h - 1 and c == w - 1:
                return 0
            res = -inf
            if r + 1 < h:
                down = grid[r + 1][c] + dp(r + 1, c, postfixCost + costMap[grid[r+1][c]])
                res = down
            if c + 1 < w:
                right = grid[r][c + 1] + dp(r, c + 1, postfixCost + costMap[grid[r][c+1]])
                res = max(res, right)
            return res
        
        ans = dp(0, 0, costMap[grid[0][0]]) + grid[0][0]
        dp.cache_clear()
        return ans if ans != -inf else -1
            

        # SOLUTION 1, prefix cost, so we have to add cost inside the dp

        # costMap = {
        #     0 : 0,
        #     1 : 1,
        #     2 : 1
        # }

        # h = len(grid)
        # w = len(grid[0])

        # @cache
        # def dp(r, c, pfCost):
        #     cost = costMap[grid[r][c]]
        #     ncost = pfCost + cost
        #     score = grid[r][c]
        #     if ncost > k:
        #         return -inf
        #     if r == h - 1 and c == w - 1:
        #         return score
        #     res = -inf
        #     if r + 1 < h:
        #         down = score + dp(r + 1, c, pfCost + cost)
        #         res = down
        #     if c + 1 < w:
        #         right = score + dp(r, c + 1, pfCost + cost)
        #         res = max(res, right)
        #     return res
        
        # ans = dp(0, 0, 0)
        # dp.cache_clear()
        # return ans if ans != -inf else -1