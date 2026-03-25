class Solution:
    def nimGame(self, piles: List[int]) -> bool:
        @cache
        def dp(t):
            if not t:
                return False
            for i in range(len(t)):
                v = t[i]
                for amt in range(1, v + 1):
                    if amt == v:
                        nt = t[:i] + t[i+1:]
                        if not dp(nt):
                            return True
                    else:
                        nt = t[:i] + (t[i]-amt,) + t[i+1:]
                        if not dp(nt):
                            return True
            return False
        
        return dp(tuple(piles))