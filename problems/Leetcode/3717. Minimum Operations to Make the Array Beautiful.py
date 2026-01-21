class Solution:
    def minOperations(self, nums: List[int]) -> int:
        @cache
        def dp(i, prev):
            if i == len(nums):
                return 0
            resHere = inf
            fullFit = nums[i] // prev
            lowStart = fullFit * prev
            if lowStart < nums[i]:
                lowStart += prev
            high = 101
            for nxt in range(lowStart, high, prev):
                diff = nxt - nums[i]
                if nxt % prev != 0:
                    continue
                resHere = min(resHere, diff + dp(i + 1, nxt))
            return resHere
        
        return dp(1, nums[0])
