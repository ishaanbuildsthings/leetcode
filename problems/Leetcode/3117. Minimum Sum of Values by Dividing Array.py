class Solution:
    def minimumValueSum(self, nums: List[int], andValues: List[int]) -> int:
        n = len(nums)
        m = len(andValues)

        @cache
        def dp(r, prefixMask, finishedSubs):
            if r == n:
                return 0 if finishedSubs == m else inf
            # still more numbers to go
            if finishedSubs == m:
                return inf
            res = inf
            nextAndTarget = andValues[finishedSubs]
            newMask = prefixMask & nums[r] if prefixMask is not None else nums[r]
            # if we truncate here
            if newMask == nextAndTarget:
                res = nums[r] + dp(r + 1, None, finishedSubs + 1)
            
            # if we keep going
            ifCont = dp(r + 1, newMask, finishedSubs)
            res = min(res, ifCont)
            return res
        
        ans = dp(0, None, 0)
        dp.cache_clear()
        return ans if ans != inf else -1