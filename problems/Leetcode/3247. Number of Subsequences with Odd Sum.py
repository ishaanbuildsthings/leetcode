class Solution:
    def subsequenceCount(self, nums: List[int]) -> int:

        # can do bottom up for O(1) space
        
        MOD = 10**9 + 7
        @cache
        def dp(i, parity):
            if i == len(nums):
                return parity
            ifTake = dp(i + 1, (parity ^ (nums[i] % 2)))
            ifSkip = dp(i + 1, parity)
            return (ifTake + ifSkip) % MOD
        return dp(0, 0)