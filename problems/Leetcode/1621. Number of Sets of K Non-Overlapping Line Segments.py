class Solution:
    def numberOfSets(self, n: int, k: int) -> int:
        MOD = (10**9) + 7
        @cache
        def dp(i, placed, open):
            if i == n:
                return 1 if placed == k and not open else 0
            if placed > k:
                return 0
            if open:
                closeHere = dp(i + 1, placed + 1, False)
                cont = dp(i + 1, placed, True)
                closeAndOpen = dp(i + 1, placed + 1, True) if i != n - 1 else 0
                return (closeHere + cont + closeAndOpen) % MOD
            stayClosed = dp(i + 1, placed, False)
            openNew = dp(i + 1, placed, True) if i != n - 1 else 0
            return (stayClosed + openNew) % MOD
        a = dp(0,0,False)
        dp.cache_clear()
        return a
            
