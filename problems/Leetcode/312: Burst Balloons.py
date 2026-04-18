class Solution:
    def maxCoins(self, nums: List[int]) -> int:
        @cache
        def dp(l, r):
            if l > r:
                return 0
            res = 0
            left = nums[l-1] if l else 1
            right = nums[r+1] if r + 1 < len(nums) else 1
            for lst in range(l, r + 1):
                newVal = dp(l, lst - 1) + dp(lst + 1, r) + (left * right * nums[lst])
                res = max(res, newVal)
            return res
        
        return dp(0, len(nums) - 1)       