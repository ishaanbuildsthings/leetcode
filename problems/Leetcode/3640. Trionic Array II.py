class Solution:
    def maxSumTrionic(self, nums: List[int]) -> int:        
        @cache
        def dp(i, stage):
            if i == len(nums):
                return -inf

            if stage == 0:
                return max(dp(i + 1, 0), nums[i] + dp(i + 1, 1))

            if stage == 1:
                if nums[i] <= nums[i-1]:
                    return -inf
                return nums[i] + max(dp(i + 1, 1), dp(i + 1, 2))

            if stage == 2:
                if nums[i] >= nums[i-1]:
                    return -inf
                return nums[i] + max(dp(i + 1, 2), dp(i + 1, 3))

            if nums[i] <= nums[i-1]:
                return -inf
            return max(nums[i], nums[i] + dp(i + 1, 3))           
            
        ans = dp(0, 0)
        dp.cache_clear()
        return ans