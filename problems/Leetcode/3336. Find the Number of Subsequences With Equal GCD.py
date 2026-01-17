class Solution:
    def subsequencePairCount(self, nums: List[int]) -> int:
        @cache
        def dp(i, gcdA, gcdB):
            if i == len(nums):
                return int(gcdA == gcdB) and gcdA is not None and gcdB is not None
            ifPutA = dp(i + 1, gcd(gcdA, nums[i]) if gcdA is not None else nums[i], gcdB)
            ifPutB = dp(i + 1, gcdA, gcd(gcdB, nums[i]) if gcdB is not None else nums[i])
            ifSkip = dp(i + 1, gcdA, gcdB)
            return ifPutA + ifPutB + ifSkip
        
        a = dp(0, None, None) % (10**9 + 7)
        dp.cache_clear()
        return a