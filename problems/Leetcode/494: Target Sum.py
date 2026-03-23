class Solution:
    def findTargetSumWays(self, nums: List[int], target: int) -> int:
        @cache
        def dp(i, tot):
            if i == len(nums):
                return int(tot == target)
            return dp(i + 1, tot + nums[i]) + dp(i + 1, tot - nums[i])
        return dp(0, 0)