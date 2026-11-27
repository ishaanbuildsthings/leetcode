class Solution:
    def minCost(self, n: int, cost: List[List[int]]) -> int:
        @cache
        def dp(l, r, leftColor, rightColor):
            if l > r:
                return 0 if leftColor != rightColor else inf
            
            resHere = inf
            for newLeft in range(3):
                for newRight in range(3):
                    if newLeft == newRight:
                        continue
                    if newLeft == leftColor:
                        continue
                    if newRight == rightColor:
                        continue
                    cLeft = cost[l][newLeft]
                    cRight = cost[r][newRight]
                    resHere = min(resHere, cLeft + cRight + dp(l + 1, r - 1, newLeft, newRight))
            
            return resHere
        
        a = dp(0, n - 1, -20, 80)
        dp.cache_clear()
        return a
                    
                    