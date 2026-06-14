class Solution:
    def maximumAmount(self, coins: List[List[int]]) -> int:
        height = len(coins)
        width = len(coins[0])
        @cache
        def dp(r, c, neuts):
            if r == height - 1 and c == width - 1:
                if coins[r][c] >= 0:
                    return coins[r][c]
                if neuts > 0:
                    return 0
                return coins[r][c]
            
            res = -inf
            
            nextCoords = []
            # go right
            if c < width - 1:
                nextCoords.append([r, c + 1])
            if r < height - 1:
                nextCoords.append([r + 1, c])
            
            for nextR, nextC in nextCoords:
                if coins[r][c] >= 0:
                    res = max(res, coins[r][c] + dp(nextR, nextC, neuts))
                elif neuts == 0:
                    res = max(res, coins[r][c] + dp(nextR, nextC, neuts))
                else:
                    ifTakeNeg = coins[r][c] + dp(nextR, nextC, neuts)
                    ifNeut = dp(nextR, nextC, neuts - 1)
                    res = max(res, ifTakeNeg, ifNeut)
            
            return res
        
        x = dp(0,0,2)
        dp.cache_clear()
        return x
                
                