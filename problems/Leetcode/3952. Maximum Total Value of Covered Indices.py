class Solution:
    def maxTotal(self, nums: List[int], s: str) -> int:
        n = len(nums)

        @cache
        def dp(i, prevCovered):
            if i == n:
                return 0
            v = nums[i]
            if s[i] == '1':
                if prevCovered:
                    return v + dp(i + 1, True)
                if i != 0:
                    moveBack = nums[i-1] + dp(i + 1, False)
                else:
                    moveBack = -inf

                stay = v + dp(i + 1, True)
                return max(moveBack, stay)

            return dp(i + 1, False)

        ans = dp(0, False)
        dp.cache_clear()
        return ans
            
            