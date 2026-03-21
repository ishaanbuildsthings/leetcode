class Solution:
    def numTilings(self, n: int) -> int:
        MOD = 10**9 + 7
        @cache
        def dp(i, isPartial):
            if i == n:
                return 1 if not isPartial else 0
            if i > n:
                return 0
            if not isPartial:
                return (dp(i + 1, False) + dp(i + 2, False) + 2 * dp(i + 1, True)) % MOD
            return (dp(i + 1, True) + dp(i + 2, False)) % MOD
        
        return dp(0, False)
            