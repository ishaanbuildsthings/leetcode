class Solution:
    def canIWin(self, maxChoosableInteger: int, desiredTotal: int) -> bool:
        if not desiredTotal:
            return True
        if sum(x for x in range(1, maxChoosableInteger + 1)) < desiredTotal:
            return False
        fmask = (1 << (maxChoosableInteger + 1)) - 1
        @cache
        def dp(taken, tot):
            if tot >= desiredTotal:
                return False
            for number in range(1, maxChoosableInteger + 1):
                if (1 << number) & taken:
                    continue
                nmask = (1 << number) | taken
                canWin = not dp(nmask, tot + number)
                if canWin:
                    return True
            return False
        
        return dp(1, 0)