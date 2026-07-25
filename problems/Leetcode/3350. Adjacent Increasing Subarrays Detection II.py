class Solution:
    def maxIncreasingSubarrays(self, nums: List[int]) -> int:
        @cache
        def descent(i):
            if i == 0:
                return 1
            if nums[i - 1] >= nums[i]:
                return 1
            return 1 + descent(i - 1)
        
        @cache
        def ascent(i):
            if i == len(nums) - 1:
                return 1
            if nums[i + 1] <= nums[i]:
                return 1
            return 1 + ascent(i + 1)
        
        res = 0
        
        for rightEdge in range(len(nums) - 1):
            res = max(res, min(descent(rightEdge), ascent(rightEdge + 1)))
            
        descent.cache_clear()
        ascent.cache_clear()
            
        return res