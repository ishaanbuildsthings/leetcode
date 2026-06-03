class Solution:
    def maximumLength(self, nums: List[int], k: int) -> int:
        # can reduce memory with a for loop
        @cache
        def dp(i, kLeft, prevTaken):
            if kLeft < 0:
                return float('-inf')
            if i == len(nums):
                return 0
            # if we take the current number
            res = 1 + dp(i + 1, kLeft - ((nums[i] != prevTaken) if prevTaken != None else 0), nums[i])
            return max(res, dp(i + 1, kLeft, prevTaken))
        res = dp(0, k, None)
        dp.cache_clear()
        return res