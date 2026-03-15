class Solution:
    def maxScore(self, a: List[int], b: List[int]) -> int:
        @cache
        def dp(i, j):
            # base case
            if i == 4:
                return 0
            if j == len(b):
                return -inf
            
            resHere = 0
            
            ifTakeHere = (b[j] * a[i]) + dp(i + 1, j + 1)
            ifSkipHere = dp(i, j + 1)
            return max(ifTakeHere, ifSkipHere)
        
        res = dp(0, 0)
        dp.cache_clear()
        return res