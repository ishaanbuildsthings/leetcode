class Solution:
    def longestSubarray(self, nums: List[int]) -> int:
        n = len(nums)
        @cache
        def decLeft(i):
            if i == 0:
                return 1
            if nums[i - 1] <= nums[i]:
                return 1 + decLeft(i - 1)
            return 1
        
        @cache
        def incRight(i):
            if i == len(nums) - 1:
                return 1
            if nums[i + 1] >= nums[i]:
                return 1 + incRight(i + 1)
            return 1
        
        res = 1
        for i in range(len(nums)):
            left = 0 if i == 0 else decLeft(i - 1)
            right = 0 if i == n - 1 else incRight(i + 1)
            res = max(res, max(left, right) + 1)
            if i and i != n - 1 and nums[i - 1] <= nums[i + 1]:
                res = max(res, 1 + left + right)
        
        return res