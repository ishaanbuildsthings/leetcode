class Solution:
    def getMoneyAmount(self, n: int) -> int:
        
        @cache
        def dp(l, r):
            if l == r:
                return 0
            if l > r:
                return 0

            resHere = inf # min amount of money needed
            for guess in range(l, r + 1):
                # if guess is wrong
                ifNeedtoGoLower = guess + dp(l, guess - 1)
                ifNeedToGoHigher = guess + dp(guess + 1, r)
                worst = max(ifNeedtoGoLower, ifNeedToGoHigher)
                resHere = min(resHere, worst)
            return resHere
        
        return dp(1, n)
