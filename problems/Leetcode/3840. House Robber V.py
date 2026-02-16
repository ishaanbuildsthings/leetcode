class Solution:
    def rob(self, nums: List[int], colors: List[int]) -> int:
        @cache
        def dp(i):
            if i == len(nums):
                return 0
            if i == len(nums) - 1:
                return nums[i]
            if colors[i + 1] == colors[i]:
                ifRob = nums[i] + dp(i + 2)
                ifSkip = dp(i + 1)
                return max(ifRob, ifSkip)
            return nums[i] + dp(i + 1)
        ans = dp(0)
        dp.cache_clear()
        return ans