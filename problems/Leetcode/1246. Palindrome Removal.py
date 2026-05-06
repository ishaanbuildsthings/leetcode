class Solution:
    def minimumMoves(self, arr: List[int]) -> int:
        @cache
        def dp(l, r):
            if l > r:
                return 0
            if l == r:
                return 1
            if l + 1 == r:
                return 1 if arr[l] == arr[r] else 2
            
            res = inf
            if arr[l] == arr[r]:
                res = dp(l + 1, r - 1)
            for allL in range(l, r):
                res = min(res, dp(l, allL) + dp(allL + 1, r))
            return res
        
        return dp(0, len(arr) - 1)